import pytest
import pandas as pd
from unittest.mock import AsyncMock, MagicMock, patch
from src.pipelines.stages.ranking_features_builder import RankingFeaturesBuilder
import os
import json
import pickle

@pytest.fixture
def dummy_artifacts(tmp_path):
    # Create dummy artifacts
    models_dir = tmp_path / "models"
    os.environ["SENTENCE_TRANSFORMERS_HOME"] = str(models_dir)
    
    for model_name in ["view_ranker", "like_ranker_v2"]:
        model_dir = models_dir / model_name
        model_dir.mkdir(parents=True)
        
        with open(model_dir / "feature_cols.json", "w") as f:
            json.dump(["course_difficulty_encoded", "course_primary_domain_encoded"], f)
            
        scaler = MagicMock()
        scaler.transform.side_effect = lambda x: x
        with open(model_dir / "scaler.pkl", "wb") as f:
            pickle.dump(scaler, f)
            
        le = MagicMock()
        le.classes_ = ["easy", "medium", "hard", "unknown"]
        le.transform.return_value = [1]
        with open(model_dir / "le_difficulty.pkl", "wb") as f:
            pickle.dump(le, f)
            
        with open(model_dir / "le_domain.pkl", "wb") as f:
            pickle.dump(le, f)
            
    yield models_dir

@pytest.mark.asyncio
async def test_ranking_features_builder(dummy_artifacts):
    session = AsyncMock()
    redis = AsyncMock()
    
    # Mock DB responses
    user_mock = MagicMock()
    user_mock.tags = []
    
    # Mock session execute
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user_mock
    
    # We will mock the internal methods to avoid complex DB mocking
    with patch.object(RankingFeaturesBuilder, '_get_user_features', return_value={
        "user_views_7d": 1.0,
        "user_likes_7d": 0.0,
        "user_views_30d": 2.0,
        "user_likes_30d": 0.0,
        "user_unique_courses_7d": 1.0,
        "user_unique_tags_7d": 1.0,
    }):
        with patch.object(RankingFeaturesBuilder, '_get_precomputed_features_bulk', return_value={
            1: {"cosine_distance": 0.5, "course_popularity_weight": 0.8}
        }):
            builder = RankingFeaturesBuilder(session, redis)
            
            # Mock courses
            course_mock = MagicMock()
            course_mock.course_id = 1
            course_mock.difficulty = "easy"
            course_mock.tags = []
            
            mock_courses_result = MagicMock()
            mock_courses_result.scalars().all.return_value = [course_mock]
            
            session.execute.side_effect = [mock_result, mock_courses_result]
            
            X_view, X_like, ordered_ids = await builder.build_features(user_id=1, candidate_ids=[1])
            
            assert ordered_ids == [1]
            assert isinstance(X_view, pd.DataFrame)
            assert isinstance(X_like, pd.DataFrame)
            assert list(X_view.columns) == ["course_difficulty_encoded", "course_primary_domain_encoded"]
            assert list(X_like.columns) == ["course_difficulty_encoded", "course_primary_domain_encoded"]
