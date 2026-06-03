import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from src.engine.embeddings import EmbeddingEngine

@pytest.fixture
def mock_sentence_transformer():
    with patch("src.engine.embeddings.SentenceTransformer") as mock:
        mock_instance = MagicMock()
        mock_instance.get_sentence_embedding_dimension.return_value = 384

        def mock_encode(text, **kwargs):
            if isinstance(text, list):
                return np.zeros((len(text), 384), dtype=np.float32)
            return np.zeros(384, dtype=np.float32)
            
        mock_instance.encode.side_effect = mock_encode
        mock.return_value = mock_instance
        yield mock

def test_embedding_engine_init(mock_sentence_transformer):
    engine = EmbeddingEngine("dummy-model")
    mock_sentence_transformer.assert_called_once_with("dummy-model")
    assert engine._EmbeddingEngine__embedding_dim == 384

def test_embedding_engine_generate(mock_sentence_transformer):
    engine = EmbeddingEngine("dummy-model")
    embedding = engine.generate("test text")
    
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (384,)
    assert embedding.dtype == np.float32

def test_embedding_engine_generate_batch(mock_sentence_transformer):
    engine = EmbeddingEngine("dummy-model")
    embeddings = engine.generate_batch(["text 1", "text 2"], batch_size=2)
    
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape == (2, 384)
    assert embeddings.dtype == np.float32
    engine._EmbeddingEngine__model.encode.assert_called_with(
        ["text 1", "text 2"],
        batch_size=2,
        convert_to_numpy=True
    )

def test_embedding_engine_prepare_course():
    result = EmbeddingEngine.prepare_course(
        name="Python 101",
        description=" Learn Python.",
        difficulty="Beginner",
        tags=["programming", "python"]
    )
    
    assert result == "Python 101 Learn Python.programming,pythonBeginner"
