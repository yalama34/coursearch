import json
import os
import pickle
import logging
from typing import Any
import pandas as pd
from datetime import datetime, timedelta

from sqlalchemy import select, func, distinct
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.association_tables import course_tags
from src.db.models import User, Course, Action


logger = logging.getLogger(__name__)

def _parse_redis_float(value: str | None) -> float:
    if value is None:
        return 0.0
    try:
        return float(value)
    except ValueError:
        return 0.0

class RankingFeaturesBuilder:
    def __init__(self, session: AsyncSession, redis: Any | None = None):
        self.__db_session = session
        self.__redis = redis
        
        models_dir = os.getenv("SENTENCE_TRANSFORMERS_HOME", "/models")

        view_dir = os.path.join(models_dir, "view_ranker")
        with open(os.path.join(view_dir, "feature_cols.json"), "r") as f:
            self.view_cols = json.load(f)
            
        with open(os.path.join(view_dir, "scaler.pkl"), "rb") as f:
            self.view_scaler = pickle.load(f)
            
        with open(os.path.join(view_dir, "le_difficulty.pkl"), "rb") as f:
            self.view_le_diff = pickle.load(f)
            
        with open(os.path.join(view_dir, "le_domain.pkl"), "rb") as f:
            self.view_le_domain = pickle.load(f)

        like_dir = os.path.join(models_dir, "like_ranker_v2")
        with open(os.path.join(like_dir, "feature_cols.json"), "r") as f:
            self.like_cols = json.load(f)
            
        with open(os.path.join(like_dir, "scaler.pkl"), "rb") as f:
            self.like_scaler = pickle.load(f)
            
        with open(os.path.join(like_dir, "le_difficulty.pkl"), "rb") as f:
            self.like_le_diff = pickle.load(f)
            
        with open(os.path.join(like_dir, "le_domain.pkl"), "rb") as f:
            self.like_le_domain = pickle.load(f)

    def _safe_transform_label(self, le, val: str | None) -> int:
        if val is None:
            val = "unknown"
        if val not in le.classes_:
            val = "unknown"
        try:
            return int(le.transform([val])[0])
        except Exception:
            return 0

    async def _get_user_features(self, user_id: int) -> dict[str, float]:
        now_ts = datetime.now()
        ts_7d = now_ts - timedelta(days=7)
        ts_30d = now_ts - timedelta(days=30)

        agg_q = (
            select(
                func.count().filter(
                    (Action.action_type == "view")
                    & (Action.timestamp >= ts_7d)
                    & (Action.timestamp < now_ts)
                ).label("user_views_7d"),
                func.count().filter(
                    (Action.action_type == "like")
                    & (Action.timestamp >= ts_7d)
                    & (Action.timestamp < now_ts)
                ).label("user_likes_7d"),
                func.count().filter(
                    (Action.action_type == "view")
                    & (Action.timestamp >= ts_30d)
                    & (Action.timestamp < now_ts)
                ).label("user_views_30d"),
                func.count().filter(
                    (Action.action_type == "like")
                    & (Action.timestamp >= ts_30d)
                    & (Action.timestamp < now_ts)
                ).label("user_likes_30d"),
            )
            .where(Action.user_id == user_id)
        )
        agg = (await self.__db_session.execute(agg_q)).one()

        uniq_courses_q = (
            select(func.count(distinct(Action.course_id)))
            .where(
                Action.user_id == user_id,
                Action.action_type == "view",
                Action.timestamp >= ts_7d,
                Action.timestamp < now_ts,
            )
        )
        user_unique_courses_7d = float((await self.__db_session.execute(uniq_courses_q)).scalar() or 0)

        uniq_tags_q = (
            select(func.count(distinct(course_tags.c.tag_id)))
            .select_from(Action)
            .join(course_tags, course_tags.c.course_id == Action.course_id)
            .where(
                Action.user_id == user_id,
                Action.action_type == "view",
                Action.timestamp >= ts_7d,
                Action.timestamp < now_ts,
            )
        )
        user_unique_tags_7d = float((await self.__db_session.execute(uniq_tags_q)).scalar() or 0)

        return {
            "user_views_7d": float(agg.user_views_7d or 0),
            "user_likes_7d": float(agg.user_likes_7d or 0),
            "user_views_30d": float(agg.user_views_30d or 0),
            "user_likes_30d": float(agg.user_likes_30d or 0),
            "user_unique_courses_7d": user_unique_courses_7d,
            "user_unique_tags_7d": user_unique_tags_7d,
        }

    async def _get_precomputed_features_bulk(
        self, user_id: int, course_ids: list[int]
    ) -> dict[int, dict[str, float]]:
        default = {"cosine_distance": 0.0, "course_popularity_weight": 0.0}
        if not self.__redis or not course_ids:
            return {cid: dict(default) for cid in course_ids}

        unique_courses = list(dict.fromkeys(course_ids))
        pipe = self.__redis.pipeline()
        for cid in course_ids:
            pipe.get(f"pair:{user_id}:{cid}:cosine_distance")
        for cid in unique_courses:
            pipe.get(f"course:{cid}:popularity")
        results = await pipe.execute()

        n_pairs = len(course_ids)
        cos_raw = results[:n_pairs]
        pop_raw = results[n_pairs:]
        pop_by_cid = {
            cid: _parse_redis_float(pop_raw[i])
            for i, cid in enumerate(unique_courses)
        }

        out: dict[int, dict[str, float]] = {}
        for i, cid in enumerate(course_ids):
            out[cid] = {
                "cosine_distance": _parse_redis_float(cos_raw[i]),
                "course_popularity_weight": pop_by_cid.get(cid, 0.0),
            }
        return out

    async def build_features(self, user_id: int, candidate_ids: list[int]) -> tuple[pd.DataFrame, pd.DataFrame, list[int]]:
        """
        Builds feature DataFrames for view_ranker and like_ranker_v2.
        """
        user_q = select(User).where(User.user_id == user_id).options(selectinload(User.tags))
        user = (await self.__db_session.execute(user_q)).scalar_one_or_none()
        if user is None:
            return pd.DataFrame(), pd.DataFrame(), []

        user_tags = {t.name for t in user.tags}
        user_tags_count = float(len(user_tags))

        user_window = await self._get_user_features(user_id=user_id)
        pair_features = await self._get_precomputed_features_bulk(user_id=user_id, course_ids=candidate_ids)

        courses_q = (
            select(Course)
            .where(Course.course_id.in_(candidate_ids))
            .options(selectinload(Course.tags))
        )
        courses = (await self.__db_session.execute(courses_q)).scalars().all()
        course_map = {c.course_id: c for c in courses}

        rows = []
        ordered_ids = []

        for cid in candidate_ids:
            course = course_map.get(cid)
            if not course:
                continue

            course_tag_set = {t.name for t in course.tags}
            common_tags = float(len(user_tags & course_tag_set))
            denom = max(1.0, float(len(user_tags) + len(course_tag_set) - common_tags))
            jaccard_tags = common_tags / denom
            course_tags_count_val = float(len(course_tag_set))

            pair_feats = pair_features.get(
                cid,
                {"cosine_distance": 0.0, "course_popularity_weight": 0.0},
            )

            row = {
                "difficulty_match": 0.0,
                "common_tags": common_tags,
                "jaccard_tags": jaccard_tags,
                "course_popularity_weight": float(pair_feats["course_popularity_weight"]),
                "cosine_distance": float(pair_feats["cosine_distance"]),
                "course_tags_count": course_tags_count_val,
                "user_views_30d": user_window["user_views_30d"],
                "user_likes_7d": user_window["user_likes_7d"],
                "user_unique_tags_7d": user_window["user_unique_tags_7d"],
                "user_unique_courses_7d": user_window["user_unique_courses_7d"],
                "user_views_7d": user_window["user_views_7d"],
                "user_likes_30d": user_window["user_likes_30d"],
                "user_tags_count": user_tags_count,

                "session_duration_hours": 0.0,
                "session_views": 0.0,
                "session_likes": 0.0,
                "session_like_rate": 0.0,
                "view_pos_in_session": 1.0,
                "time_since_last_like_hours": 0.0,
                "user_views_1h": 0.0,
                "user_views_4h": 0.0,
                "user_activity_ratio_7d_30d": 0.0,
                "user_like_rate_30d": 0.0,
                "user_tags_entropy": 0.0,
                "user_domain_count": 0.0,
                "days_since_last_action": 0.0,
                "user_views_prev_7d": 0.0,
                "user_views_trend": 0.0,
                "user_session_length_avg": 0.0,
                "user_session_activity_30min": 0.0,
                "user_conversion_ratio": 0.0,
                "course_views_7d": 0.0,
                "course_views_30d": 0.0,
                "course_likes_7d": 0.0,
                "course_likes_30d": 0.0,
                "course_like_rate": 0.0,
                "course_trend": 0.0,
                "course_age_days": 0.0,
                "cooc_sum": 0.0,
                "cooc_mean": 0.0,
                "cooc_max": 0.0,
                "domain_jaccard": 0.0,
                "cluster_jaccard": 0.0,
                "primary_domain_match": 0.0,
                "dot_product": 0.0,
                "l2_distance": 0.0,
                "max_cosine_to_recent_likes": 0.0,
                "mean_cosine_to_recent_views": 0.0,
                "max_jaccard_to_recent_likes": 0.0,
                "viewed_before": 0.0,
                "times_viewed_before": 0.0,
                "liked_before": 0.0,
                "last_interaction_days": 0.0,
                "view_number": 1.0,
                "hours_since_prev_view": 0.0,
            }

            row["course_difficulty_encoded_view"] = self._safe_transform_label(self.view_le_diff, course.difficulty)
            row["course_primary_domain_encoded_view"] = self._safe_transform_label(self.view_le_domain, "unknown") # No domain in Course yet
            
            row["course_difficulty_encoded_like"] = self._safe_transform_label(self.like_le_diff, course.difficulty)
            row["course_primary_domain_encoded_like"] = self._safe_transform_label(self.like_le_domain, "unknown")

            rows.append(row)
            ordered_ids.append(cid)

        if not rows:
            return pd.DataFrame(), pd.DataFrame(), []

        df = pd.DataFrame(rows)

        view_df = df.copy()
        view_df["course_difficulty_encoded"] = view_df["course_difficulty_encoded_view"]
        view_df["course_primary_domain_encoded"] = view_df["course_primary_domain_encoded_view"]
        X_view = view_df[self.view_cols]
        X_view_scaled = self.view_scaler.transform(X_view)

        like_df = df.copy()
        like_df["course_difficulty_encoded"] = like_df["course_difficulty_encoded_like"]
        like_df["course_primary_domain_encoded"] = like_df["course_primary_domain_encoded_like"]
        X_like = like_df[self.like_cols]
        X_like_scaled = self.like_scaler.transform(X_like)

        return X_view_scaled, X_like_scaled, ordered_ids
