import logging

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.recommendations import RecommendationItem
from src.protocols.recommendation_stage import RecommendationStage
from src.domain.recommendation.pipeline_order import DEFAULT_RECOMMENDATION_PIPELINE_ORDER
from src.domain.recommendation.stages_factory import STAGES_FACTORY


logger = logging.getLogger(__name__)

class RecommendationPipeline:
    def __init__(self, session: AsyncSession, stages: list[RecommendationStage] | None = None):
        self.__db_session: AsyncSession = session
        self.stages: list[RecommendationStage] | None = stages if stages is not None else []

    async def execute(self, user_id: int, limit: int = 10) -> list[RecommendationItem]:
        """
        Execute the recommendation pipeline
        :param user_id:
        :param limit:
        :return:
        """
        candidates: list[RecommendationItem] = []

        for stage in self.stages:
            logger.info(f"Executing stage {stage.name}")
            stage_response = await stage.process(user_id=user_id, candidates=candidates, limit=limit)
            candidates = stage_response
            logger.info(f"Got {len(candidates)} candidates for stage {stage.name}")

        if len(candidates) == 0:
            logger.info(f"Got no candidates from pipeline")
            raise HTTPException(status_code=404, detail="No candidates found")

        return candidates

    def _add_stage(self, stage: object) -> None:
        """
        Add a stage to the pipeline following the protocol
        The stage will be added to the pipeline and will become the last stage of the pipeline
        :param stage:
        :return:
        """
        if not isinstance(stage, RecommendationStage):
            raise TypeError("Stage must be of type Recommendationstage")

        self.stages.append(stage)

    async def register_pipeline(self, stages_order = DEFAULT_RECOMMENDATION_PIPELINE_ORDER) -> None:
        """
        Register the recommendation pipeline by the given order.
        If order is not given uses the ``DEFAULT_RECOMMENDATION_PIPELINE_ORDER``
        :param stages_order:
        :return:
        """
        self.stages.clear()

        logger.info(f"Registering recommendation pipeline for stages {stages_order}")

        for stage in stages_order:
            cur_stage_factory = STAGES_FACTORY[stage]
            cur_stage = cur_stage_factory(self.__db_session)
            self._add_stage(cur_stage)
