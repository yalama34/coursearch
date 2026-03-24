from typing import List
from numpy.typing import NDArray
import numpy as np

from sentence_transformers import SentenceTransformer


class EmbeddingEngine:
    def __init__(self, model_path: str) -> None:
        self.__model = SentenceTransformer(model_path)
        self.__embedding_dim: int = self.__model.get_sentence_embedding_dimension()

    def generate(self, text: str) -> NDArray[np.float32]:
        """
        Генерирует эмбеддинг для строки
        :param text: строка
        :return: Представление строки в векторном пространстве
        """
        embedding: NDArray[np.float32]  = self.__model.encode(
            text,
            convert_to_numpy=True
        )
        return embedding

    def generate_batch(self, texts: List[str], batch_size: int = 32) -> NDArray[np.float32]:
        """
        Генерирует эмбеддини для списка строк
        :param texts: список строк
        :param batch_size: размер кучи, котор
        :return: Список представлений строк в векторном пространтсве
        """
        embeddings: NDArray[np.float32] = self.__model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True
        )
        return embeddings