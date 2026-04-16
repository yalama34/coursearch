from typing import Protocol, runtime_checkable

from src.schemas.recommendations import RecommendationItem

@runtime_checkable
class RecommendationStage(Protocol):
    @property
    def stage_name(self) -> str:
        """
        Returns the name of the stage that is currently being processed
        :return: The name of the stage that is currently being processed
        """
        ...

    async def process(
            self,
            user_id: int,
            candidates: list[RecommendationItem],
            limit: int = 10
    ) -> list[RecommendationItem]:
        """
        Starts the current stage of the recommendation process
        :param user_id: id of the user
        :param limit: maximum number of recommendations to return
        :param candidates: list of candidates
        :return:list of `RecommendationItem`
        """
        ...
