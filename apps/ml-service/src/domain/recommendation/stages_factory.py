from src.domain.recommendation.pipeline_order import StageName
from src.pipelines.stages.content_based_stage import ContentBasedStage
from src.pipelines.stages.top_n_stage import TopNStage
from src.pipelines.stages.like_ranker_stage import LikeRankerStage


STAGES_FACTORY = {
    StageName.TOP_N: TopNStage,
    StageName.CONTENT_BASED: ContentBasedStage,
    StageName.LIKE_RANKER: LikeRankerStage
}
