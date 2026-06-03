import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from src.pipelines.recommendation_pipeline import RecommendationPipeline
from src.protocols.recommendation_stage import RecommendationStage
from src.schemas.recommendations import RecommendationItem
from src.domain.recommendation.pipeline_order import StageName

class MockStage:
    def __init__(self, name, return_candidates):
        self._stage_name = name
        self.return_candidates = return_candidates
        self.process = AsyncMock(return_value=self.return_candidates)
        
    @property
    def stage_name(self) -> str:
        return self._stage_name

@pytest.mark.asyncio
async def test_recommendation_pipeline_execute(mock_session, mock_redis):
    candidates_stage1 = [RecommendationItem(item_id=1)]
    candidates_stage2 = [RecommendationItem(item_id=1)]
    
    stage1 = MockStage("stage1", candidates_stage1)
    stage2 = MockStage("stage2", candidates_stage2)
    
    pipeline = RecommendationPipeline(session=mock_session, redis=mock_redis, stages=[stage1, stage2])
    
    result = await pipeline.execute(user_id=123, limit=5)
    
    assert result == candidates_stage2
    stage1.process.assert_called_once_with(user_id=123, candidates=[], limit=5)
    stage2.process.assert_called_once_with(user_id=123, candidates=candidates_stage1, limit=5)

@pytest.mark.asyncio
async def test_recommendation_pipeline_execute_empty(mock_session):
    stage1 = MockStage("stage1", [])
    pipeline = RecommendationPipeline(session=mock_session, stages=[stage1])
    
    with pytest.raises(HTTPException) as exc_info:
        await pipeline.execute(user_id=123)
        
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "No candidates found"

def test_recommendation_pipeline_add_stage(mock_session):
    pipeline = RecommendationPipeline(session=mock_session)
    stage = MockStage("stage1", [])
    
    pipeline._add_stage(stage)
    assert len(pipeline.stages) == 1
    assert pipeline.stages[0] == stage
    
    with pytest.raises(TypeError):
        pipeline._add_stage("not a stage")

@pytest.mark.asyncio
async def test_recommendation_pipeline_register(mock_session, mock_redis):
    pipeline = RecommendationPipeline(session=mock_session, redis=mock_redis)
    
    mock_stage_instance = MockStage("mock", [])
    mock_factory = MagicMock(return_value=mock_stage_instance)
    
    with patch.dict("src.pipelines.recommendation_pipeline.STAGES_FACTORY", {StageName.CONTENT_BASED: mock_factory}, clear=True):
        await pipeline.register_pipeline([StageName.CONTENT_BASED])
        
        assert len(pipeline.stages) == 1
        assert pipeline.stages[0] == mock_stage_instance
        mock_factory.assert_called_once_with(mock_session)
