import os
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Any

from catboost import CatBoostRanker
from sqlalchemy import select, func, distinct
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.recommendation.pipeline_order import StageName
from src.db.models.association_tables import course_tags
from src.schemas.recommendations import RecommendationItem, RecommendationExplanation
from src.db.models import User, Course, Action

logger = logging.getLogger(__name__)

FEATURE_COLS = [
    "difficulty_match",
    "common_tags",
    "jaccard_tags",
    "course_popularity_weight",
    "cosine_distance",
    "course_tags_count",
    "user_views_30d",
    "user_likes_7d",
    "user_unique_tags_7d",
    "user_unique_courses_7d",
    "user_views_7d",
    "user_likes_30d",
    "user_tags_count",
]


def _parse_redis_float(value: str | None) -> float:
    if value is None:
        return 0.0
    try:
        return float(value)
    except ValueError:
        return 0.0


class LikeRankerStage:
    def __init__(self, session: AsyncSession, redis: Any | None = None):
        self.__db_session = session
        self.__redis = redis
        self.__model_path = os.getenv("SENTENCE_TRANSFORMERS_HOME", "/models") + "/like_ranker/model.cbm"
        self.__model = CatBoostRanker()
        self.__model.load_model(self.__model_path)

    @property
    def stage_name(self) -> str:
        return StageName.LIKE_RANKER

    async def _get_user_features(self, user_id: int) -> dict[str, float]:
        """
        Retrieves user activity features over 7-day and 30-day windows
        :param user_id:
        :return:
        """
        now_ts = datetime.utcnow()
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
        """
        Load cosine distance (per user-course pair) and course popularity from Redis.
        Keys: ``pair:{user_id}:{course_id}:cosine_distance``, ``course:{course_id}:popularity``.
        """
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

    async def process(self, user_id: int, candidates: list[RecommendationItem], limit: int = 10) -> list[RecommendationItem]:
        """
        Processes and ranks the candidate courses for a given user
        :param user_id:
        :param candidates:
        :param limit:
        :return:
        """
        logger.info(f"[{self.stage_name}] Starting LikeRankerStage for user_id={user_id}. Candidates count: {len(candidates) if candidates else 0}, limit={limit}")

        if not candidates:
            logger.info(f"[{self.stage_name}] Got no candidates for user_id={user_id}")
            return candidates

        user_q = select(User).where(User.user_id == user_id).options(selectinload(User.tags))
        user = (await self.__db_session.execute(user_q)).scalar_one_or_none()
        if user is None:
            logger.info(f"[{self.stage_name}] Couldn't find user in db. user_id={user_id}")
            return candidates

        user_tags = {t.name for t in user.tags}
        user_tags_count = float(len(user_tags))

        user_window = await self._get_user_features(user_id=user_id)

        candidate_ids = [c.item_id for c in candidates]
        pair_features = await self._get_precomputed_features_bulk(
            user_id=user_id, course_ids=candidate_ids
        )
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
            course_tags_count = float(len(course_tag_set))

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
                "course_tags_count": course_tags_count,
                "user_views_30d": user_window["user_views_30d"],
                "user_likes_7d": user_window["user_likes_7d"],
                "user_unique_tags_7d": user_window["user_unique_tags_7d"],
                "user_unique_courses_7d": user_window["user_unique_courses_7d"],
                "user_views_7d": user_window["user_views_7d"],
                "user_likes_30d": user_window["user_likes_30d"],
                "user_tags_count": user_tags_count,
            }

            rows.append(row)
            ordered_ids.append(cid)

        if not rows:
            return candidates

        X = pd.DataFrame(rows)[FEATURE_COLS]
        scores = self.__model.predict(X)

        score_map = {cid: float(score) for cid, score in zip(ordered_ids, scores)}
        ranked = sorted(candidates, key=lambda c: score_map.get(c.item_id, -1e12), reverse=True)[:limit]

        for item in ranked:
            score = score_map.get(item.item_id)
            if item.explanation is None:
                item.explanation = RecommendationExplanation(
                    text="Рекомендовано с учетом вероятности лайка",
                    confidence=score,
                )
            else:
                item.explanation.confidence = score

        logger.info(f"[{self.stage_name}] Finished LikeRankerStage for user_id={user_id}. Returned {len(ranked)} items.")
        return ranked
