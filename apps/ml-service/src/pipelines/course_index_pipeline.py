from typing import Any, Dict, List
import os

import numpy as np
from numpy.typing import NDArray
from sqlalchemy.ext.asyncio import AsyncSession

from ..services.course_services import iterate_courses_with_tags
from ..utils.mappers import normalized_tag_strings
from ..engine.chroma_client import ChromaClient
from ..engine.embeddings import EmbeddingEngine


current_dir_path = os.path.dirname(os.path.realpath(__file__))
model_path = os.path.join(current_dir_path, "..", "models", "it-slang-model-v4")


LIMIT = 200


class CourseIndexPipeline:
    """
    Load courses from SQL, embed them with the domain-tuned model, and upsert into Chroma.
    Also supports content-based recommendations from a user's tag profile embedding.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        :param session: Async SQLAlchemy session for repository calls.
        """
        self.__model_path = os.getenv("SENTENCE_TRANSFORMERS_HOME") + "/course-emb-v1"
        self.__db_session: AsyncSession = session
        self.__chroma_client = ChromaClient()
        self.__embedding_engine = EmbeddingEngine(self.__model_path)

    async def index_all_courses(self) -> None:
        """
        Paginate through all courses in batches via ``iterate_courses_with_tags``,
        build embedding texts, compute vectors, and upsert into Chroma.
        :return: None
        """
        async for batch in iterate_courses_with_tags(
            self.__db_session, batch_size=LIMIT
        ):
            courses_with_tags: List[tuple[dict, List[str]]] = [
                (course, normalized_tag_strings(course)) for course in batch
            ]

            courses_texts = [
                self.__embedding_engine.prepare_course(
                    name=course["name"],
                    description=course.get("description") or "",
                    difficulty=course.get("difficulty") or "",
                    tags=tags,
                )
                for course, tags in courses_with_tags
            ]

            list_of_embeddings: NDArray[np.float32] = self.__embedding_engine.generate_batch(
                courses_texts
            )
            embeddings: List[NDArray[np.float32]] = [
                np.asarray(list_of_embeddings[i], dtype=np.float32)
                for i in range(list_of_embeddings.shape[0])
            ]

            ids: List[str] = [str(course["course_id"]) for course, _ in courses_with_tags]
            metadatas: List[Dict[str, Any]] = [
                {
                    "course_id": int(course["course_id"]),
                    "difficulty": str(course["difficulty"])
                    if course.get("difficulty") is not None
                    else "",
                    "tags": ",".join(tags),
                }
                for course, tags in courses_with_tags
            ]

            self.__chroma_client.upsert_courses(
                ids=ids,
                names=courses_texts,
                embeddings=embeddings,
                metadatas=metadatas,
            )