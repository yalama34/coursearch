from enum import StrEnum


class StageName(StrEnum):
    TOP_N = "top_n_stage"
    CONTENT_BASED = "content_based_stage"
    LIKE_RANKER = "like_ranker_stage"

DEFAULT_RECOMMENDATION_PIPELINE_ORDER = [
    StageName.CONTENT_BASED,
    StageName.TOP_N,
    StageName.LIKE_RANKER,
]
