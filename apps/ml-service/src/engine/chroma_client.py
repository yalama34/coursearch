from typing import List, Dict, Optional


import chromadb
import numpy as np
from chromadb.types import Collection
from chromadb import QueryResult
from numpy.typing import NDArray


class ChromaClient:
    def __init__(self) -> None:
        """
        Create an in-memory Chroma client and ensure the ``courses`` collection exists.
        Vectors use cosine distance (``hnsw:space`` = cosine).
        """
        self.__chroma_client = chromadb.Client()
        self.__collection: Collection = self.__chroma_client.get_or_create_collection(
            name="courses",
            metadata={"hnsw:space": "cosine"}
        )

    def upsert_courses(self, ids: List[str], names: List[str],
                       embeddings: List[NDArray[np.float32]], metadatas: List[Dict]) -> None:
        """
        Upsert course vectors and metadata into the Chroma collection.
        :param ids: Unique string IDs for each course (e.g. stringified course_id).
        :param names: Document strings stored alongside vectors (often the same text used for embedding).
        :param embeddings: One float32 embedding vector per course, same order as ids.
        :param metadatas: Per-course metadata dicts (Chroma-compatible scalar values only).
        :return: None
        """
        self.__collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=names,
            metadatas=metadatas
        )

    def search_similar(self, query_embeddings: List[float], filters: Optional[Dict[str, str | int]]= None,
                       n_results: Optional[int] = None) -> List[str]:
        """
        Query the collection for courses nearest to the given embedding(s).
        :param query_embeddings: Flat embedding (list of floats) or batch format expected by Chroma's query API.
        :param filters: Optional Chroma ``where`` metadata filter; None means no filter.
        :param n_results: Number of nearest neighbors to return per query (default 10).
        :return: List of course IDs for the first query, most similar first (string IDs as stored in Chroma).
        """
        query_result: QueryResult = self.__collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results if n_results is not None else 10,
            where=filters if filters is not None else None,
        )

        course_ids: List[str] = query_result["ids"][0] if query_result["ids"] else []
        return course_ids
