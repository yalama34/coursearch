from typing import Any, Dict, List, Optional
import os


import numpy as np
from numpy.typing import NDArray


from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession


from ..db.repositories import get_courses_with_tags_raw, get_course_by_id
from ..db.models import Course, User, Tag
from ..engine.chroma_client import ChromaClient
from ..engine.embeddings import EmbeddingEngine


current_dir_path = os.path.dirname(os.path.realpath(__file__))
model_path = os.path.join(current_dir_path, "..", "models", "it-slang-model-v4")


LIMIT = 200


class CourseEmbeddingPipeline:
    """
    Load courses from SQL, embed them with the domain-tuned model, and upsert into Chroma.
    Also supports content-based recommendations from a user's tag profile embedding.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        :param session: Async SQLAlchemy session for repository calls.
        """
        self.__db_session: AsyncSession = session
        self.__chroma_client = ChromaClient()
        self.__embedding_engine = EmbeddingEngine(model_path)

    async def index_all_courses(self) -> None:
        """
        Paginate through all courses (``LIMIT`` rows per batch), build embedding texts,
        compute vectors, and upsert ids, documents, embeddings, and metadata into Chroma.
        :return: None
        """
        offset = 0

        while True:
            courses_from_db: List[Row[Any]] = await get_courses_with_tags_raw(
                session=self.__db_session, limit=LIMIT, offset=offset
            )
            if not courses_from_db:
                break

            rows_with_tags: List[tuple[Row[Any], List[str]]] = []
            for row in courses_from_db:
                raw_tags = list(row.tags) if row.tags is not None else []
                tag_list = [str(tag) for tag in raw_tags if tag is not None]
                rows_with_tags.append((row, tag_list))

            courses_texts = [
                self.__embedding_engine.prepare_course(
                    name=row.name,
                    description=row.description or "",
                    difficulty=row.difficulty or "",
                    tags=tags,
                )
                for row, tags in rows_with_tags
            ]

            list_of_embeddings: NDArray[np.float32] = self.__embedding_engine.generate_batch(courses_texts)
            embeddings: List[NDArray[np.float32]] = [
                np.asarray(list_of_embeddings[i], dtype=np.float32) for i in range(list_of_embeddings.shape[0])
            ]

            ids: List[str] = [str(row.course_id) for row, tags in rows_with_tags]
            metadatas: List[Dict[str, Any]] = [
                {
                    "course_id": int(row.course_id),
                    "difficulty": str(row.difficulty) if row.difficulty is not None else "",
                    "tags": ",".join(tags),
                }
                for row, tags in rows_with_tags
            ]

            self.__chroma_client.upsert_courses(
                ids=ids,
                names=courses_texts,
                embeddings=embeddings,
                metadatas=metadatas,
            )

            offset += LIMIT

    async def get_content_based_recommendations(
        self,
        user: User,
        filters: Optional[Dict[str, str | int]] = None,
        num_courses: Optional[int] = 10,
    ) -> List[Optional[Course]]:
        """
        Embed the user's tags as one space-separated string, query Chroma for similar courses,
        then load full ``Course`` rows from the database by returned IDs.
        :param user: User ORM instance with a ``tags`` relation (each tag has ``name``).
        :param filters: Optional Chroma metadata filter passed to ``search_similar``.
        :param num_courses: Maximum number of recommendations to retrieve.
        :return: List of ``Course`` rows; entries are ``None`` if Chroma returns an id with no matching row.
        """
        tags: List[Tag] = user.tags or []
        user_text = " ".join(tag.name for tag in tags)
        user_embeddings: NDArray[np.float32] = self.__embedding_engine.generate(user_text)

        recommended_course_ids: List[str] = self.__chroma_client.search_similar(
            query_embeddings=user_embeddings.tolist(),
            filters=filters if filters is not None else None,
            n_results=num_courses,
        )

        recommended_courses: List[Optional[Course]] = []

        for course_id_raw in recommended_course_ids:
            course: Optional[Course] = await get_course_by_id(self.__db_session, int(course_id_raw))
            if course is not None:
                recommended_courses.append(course)

        return recommended_courses