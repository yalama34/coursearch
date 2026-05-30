import os
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from numpy.typing import NDArray
import numpy as np

from src.schemas.recommendations import RecommendationItem, RecommendationExplanation
from src.domain.recommendation.pipeline_order import StageName
from src.engine.chroma_client import ChromaClient
from src.engine.embeddings import EmbeddingEngine
from src.db.models import Course, User


logger = logging.getLogger(__name__)

class ContentBasedStage:
    def __init__(self, session: AsyncSession):
        self.__model_path = os.getenv("SENTENCE_TRANSFORMERS_HOME", "/models") + "/course-emb-v1"
        self.__db_session: AsyncSession = session
        self.__chroma_client = ChromaClient()
        self.__embedding_engine = EmbeddingEngine(self.__model_path)

    @property
    def stage_name(self) -> str:
        return StageName.CONTENT_BASED

    async def process(
            self,
            user_id: int,
            candidates: list[RecommendationItem],
            limit: int = 10
    ) -> list[RecommendationItem]:
        """
        If ``candidates`` is empty finds the needed candidates in all db.
        If ``candidates`` is not empty reranking it by relevancy.
        :param user_id:
        :param candidates:
        :param limit:
        :return:
        """
        logger.info(f"[{self.stage_name}] Starting ContentBasedStage for user_id={user_id}. Candidates count: {len(candidates) if candidates else 0}, limit={limit}")

        query = select(User).where(User.user_id == user_id).options(selectinload(User.tags))
        result = await self.__db_session.execute(query)
        user = result.scalar_one_or_none()

        if not user or not user.tags:
            logger.info("No tags found for user %s", user_id)
            return candidates

        user_tags_list = [tag.name for tag in user.tags]
        user_text = " ".join(user_tags_list)
        user_embeddings: NDArray[np.float32] = self.__embedding_engine.generate(user_text)

        filters = None

        if candidates:
            logger.info(f"[{self.stage_name}] Got candidates from previous stage. Reranking them...")
            candidate_ids = [int(c.item_id) for c in candidates]

            if len(candidate_ids) == 1:
                filters = {"course_id": candidate_ids[0]}
            else:
                filters = {"course_id": {"$in": candidate_ids}}

        recommended_courses_id_str = self.__chroma_client.search_similar(
            query_embeddings=user_embeddings,
            filters=filters,
            n_results=limit
        )

        final_course_ids = []
        for cid_str in recommended_courses_id_str:
            if len(final_course_ids) >= limit:
                break
            final_course_ids.append(int(cid_str))

        for candidate in candidates:
            if len(final_course_ids) >= limit:
                break
            if candidate.item_id not in final_course_ids:
                final_course_ids.append(candidate.item_id)
        if not final_course_ids:
            logger.info(f"[{self.stage_name}] No courses found for user %s", user_id)
            return []

        courses_query = (
            select(Course)
            .where(Course.course_id.in_(final_course_ids))
            .options(selectinload(Course.tags))
        )
        courses_result = await self.__db_session.execute(courses_query)
        courses_db = courses_result.scalars().all()

        result_candidates = []

        for cid in final_course_ids:
            existing_candidate = next((c for c in candidates if c.item_id == cid), None)
            old_confidence = existing_candidate.explanation.confidence if existing_candidate and existing_candidate.explanation else None

            explanation = RecommendationExplanation(
                text="",
                confidence=old_confidence
            )

            item = RecommendationItem(item_id=cid, explanation=explanation)
            result_candidates.append(item)

        logger.info(f"[{self.stage_name}] Finished ContentBasedStage for user_id={user_id}.\nReturned {len(result_candidates)} items")
        return result_candidates
