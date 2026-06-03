import pytest
import pandas as pd
from unittest.mock import AsyncMock, MagicMock, patch
from src.pipelines.stages.like_ranker_stage import LikeRankerStage
from src.schemas.recommendations import RecommendationItem

@pytest.mark.asyncio
async def test_like_ranker_stage_blend():
    session = AsyncMock()
    redis = AsyncMock()
    
    with patch('src.pipelines.stages.like_ranker_stage.RankingFeaturesBuilder') as MockBuilder:
        with patch('src.pipelines.stages.like_ranker_stage.CatBoostRanker') as MockRanker:
            # Setup mock builder
            mock_builder_instance = MockBuilder.return_value
            X_view_scaled = pd.DataFrame()
            X_like_scaled = pd.DataFrame()
            ordered_ids = [1, 2, 3]
            mock_builder_instance.build_features.return_value = (X_view_scaled, X_like_scaled, ordered_ids)
            
            # Setup mock models
            mock_view_model = MagicMock()
            mock_like_model = MagicMock()
            MockRanker.side_effect = [mock_view_model, mock_like_model]
            
            # Mock predictions
            import numpy as np
            mock_view_model.predict.return_value = np.array([0.1, 0.9, 0.5])
            mock_like_model.predict.return_value = np.array([0.8, 0.2, 0.5])
            
            stage = LikeRankerStage(session, redis)
            stage.weight_view = 0.5
            stage.weight_like = 0.5
            
            candidates = [
                RecommendationItem(item_id=1),
                RecommendationItem(item_id=2),
                RecommendationItem(item_id=3)
            ]
            
            ranked = await stage.process(user_id=1, candidates=candidates)
            
            assert len(ranked) == 3
            # view_norm: [0, 1, 0.5]
            # like_norm: [1, 0, 0.5]
            # combined: [0.5, 0.5, 0.5]
            # So all scores should be 0.5
            for item in ranked:
                assert item.explanation.confidence == 0.5
