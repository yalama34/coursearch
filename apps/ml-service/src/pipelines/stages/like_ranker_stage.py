import os
import logging
from typing import Any

from catboost import CatBoostRanker
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.recommendation.pipeline_order import StageName
from src.schemas.recommendations import RecommendationItem, RecommendationExplanation
from src.pipelines.stages.ranking_features_builder import RankingFeaturesBuilder


logger = logging.getLogger(__name__)

class LikeRankerStage:
    def __init__(self, session: AsyncSession, redis: Any | None = None):
        self.__db_session = session
        self.__redis = redis
        
        self.features_builder = RankingFeaturesBuilder(session, redis)
        
        models_dir = os.getenv("SENTENCE_TRANSFORMERS_HOME", "/models")

        self.view_model = CatBoostRanker()
        self.view_model.load_model(os.path.join(models_dir, "view_ranker", "catboost_ranker.cbm"))

        self.like_model = CatBoostRanker()
        self.like_model.load_model(os.path.join(models_dir, "like_ranker_v3", "catboost_ranker.cbm"))

        self.weight_view = float(os.getenv("RANK_BLEND_VIEW_WEIGHT", "0.5"))
        self.weight_like = float(os.getenv("RANK_BLEND_LIKE_WEIGHT", "0.5"))

    @property
    def stage_name(self) -> str:
        return StageName.LIKE_RANKER

    def _normalize_scores(self, scores: list[float]) -> list[float]:
        if not scores:
            return []
        min_s = min(scores)
        max_s = max(scores)
        if max_s == min_s:
            return [0.5 for _ in scores]
        return [(s - min_s) / (max_s - min_s) for s in scores]

    async def process(self, user_id: int, candidates: list[RecommendationItem], limit: int = 10) -> list[RecommendationItem]:
        """
        Processes and ranks the candidate courses for a given user
        """
        logger.info(f"[{self.stage_name}] Starting LikeRankerStage for user_id={user_id}. Candidates count: {len(candidates) if candidates else 0}, limit={limit}")

        if not candidates:
            logger.info(f"[{self.stage_name}] Got no candidates for user_id={user_id}")
            return candidates

        candidate_ids = [c.item_id for c in candidates]
        
        X_view_scaled, X_like_scaled, ordered_ids = await self.features_builder.build_features(user_id, candidate_ids)
        
        if not ordered_ids:
            return candidates

        view_scores = self.view_model.predict(X_view_scaled)
        like_scores = self.like_model.predict(X_like_scaled)

        norm_view = self._normalize_scores(view_scores.tolist())
        norm_like = self._normalize_scores(like_scores.tolist())

        score_map = {}
        for i, cid in enumerate(ordered_ids):
            combined = self.weight_view * norm_view[i] + self.weight_like * norm_like[i]
            score_map[cid] = combined

        ranked = sorted(candidates, key=lambda c: score_map.get(c.item_id, -1e12), reverse=True)[:limit]

        for item in ranked:
            score = score_map.get(item.item_id)
            if item.explanation is None:
                item.explanation = RecommendationExplanation(
                    text="Рекомендовано с учетом вероятности просмотра и лайка",
                    confidence=score,
                )
            else:
                item.explanation.confidence = score

        logger.info(f"[{self.stage_name}] Finished LikeRankerStage for user_id={user_id}. Returned {len(ranked)} items.")
        return ranked
