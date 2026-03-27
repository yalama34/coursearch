from typing import List


from numpy.typing import NDArray
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingEngine:
    def __init__(self, model_path: str) -> None:
        """
        Load a SentenceTransformer model from disk or Hugging Face hub path.
        :param model_path: Path to the model directory or model identifier.
        """
        self.__model = SentenceTransformer(model_path)
        self.__embedding_dim: int = self.__model.get_sentence_embedding_dimension()

    def generate(self, text: str) -> NDArray[np.float32]:
        """
        Encode a single string into an embedding vector.
        :param text: Input text.
        :return: 1-D NumPy array of dtype float32 in the model embedding space.
        """
        embedding: NDArray[np.float32]  = self.__model.encode(
            text,
            convert_to_numpy=True
        )
        return embedding

    def generate_batch(self, texts: List[str], batch_size: int = 32) -> NDArray[np.float32]:
        """
        Encode a list of strings into embedding vectors in batches.
        :param texts: List of input strings.
        :param batch_size: Number of texts encoded per forward pass.
        :return: 2-D NumPy array of shape (len(texts), embedding_dim), dtype float32.
        """
        embeddings: NDArray[np.float32] = self.__model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True
        )
        return embeddings

    @staticmethod
    def prepare_course(name: str, description: str, difficulty: str, tags: List[str]) -> str:
        """
        Concatenate course fields into one string for embedding.
        :param name: Course title.
        :param description: Course description text.
        :param difficulty: Difficulty label or level.
        :param tags: List of tag names.
        :return: Single string combining all fields (no separators between segments except tags CSV).
        """
        tags_str = ",".join(tags)
        result = name + description + tags_str + difficulty

        return result
