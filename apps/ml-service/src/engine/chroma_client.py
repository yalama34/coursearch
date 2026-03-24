import chromadb
import numpy as np


from chromadb.types import Collection
from chromadb import QueryResult
from typing import List, Dict, Optional
from numpy.typing import NDArray


class ChromaClient:
    def __init__(self):
        self.__chroma_client = chromadb.Client()
        self.__collection: Collection = self.__chroma_client.get_or_create_collection(
            name="courses",
            metadata={"hnsw:space": "cosine"}
        )

    def upsert_courses(self, ids: List[str], names: List[str],
                       embeddings: List[NDArray[np.float32]], metadatas: List[Dict]) -> None:
        """
        Добавление указанные курсы курсы в коллекцию ChromaDB
        :param ids: идентификаторы курсов
        :param names: названия курсов
        :param embeddings: эмбеддинги, сгенерированные моделью по курсу
        :param metadatas: метаданные
        :return: None
        """
        self.__collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=names,
            metadatas=metadatas
        )

    def search_similar(self, query_embeddings: List[float], filters: Optional[Dict[str, str | int]]= None,
                       n_results: Optional[int] = None) -> List[int]:
        """
        Поиск похожих курсов
        :param query_embeddings: эмбеддинги, по которым будет производиться поиск похожих курсов
        :param filters: фильтры поиска
        :param n_results: количество результатов
        :return: список идентификаторов курсов, начиная с более близкого по значению
        """
        query_result: QueryResult = self.__collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results if n_results is not None else 10,
            where=filters if filters is not None else {},
        )

        course_ids: List[int] = query_result["ids"][0] if query_result["ids"] else []
        return course_ids
