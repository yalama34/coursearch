import logging
from typing import Any, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import RECOMMENDATIONS_CACHE_TTL_SECONDS
from src.db.models.user import User
from src.db.models.course import Course
from src.schemas.recommendations import ExplanationItem, ExplanationsResponse
from src.integrations.llm.services.explanation import LLMExplanation
from src.utils.user_profile import build_user_profile_text


logger = logging.getLogger(__name__)

def _explanation_cache_key(user_id: int, course_id: int) -> str:
    return f"explanation:user:{user_id}:course:{course_id}"


async def get_explanations(
    user_id: int,
    course_ids: List[int],
    session: AsyncSession,
    redis: Any | None = None,
    force: bool = False,
) -> ExplanationsResponse:
    """
    Get explanations for a list of course IDs for a specific user.
    Checks Redis cache first. For cache misses, fetches user and course data,
    calls LLM to generate explanations, caches them, and returns the combined results.
    """
    if not course_ids:
        return ExplanationsResponse(user_id=user_id, explanations=[])

    cached_explanations = {}
    missing_ids = list(course_ids)

    if force and redis is not None:
        try:
            keys = [_explanation_cache_key(user_id, cid) for cid in course_ids]
            if keys:
                await redis.delete(*keys)
        except Exception as e:
            logger.error(f"Error clearing explanation cache: {e}")

    if redis is not None and not force:
        missing_ids = []
        try:
            keys = [_explanation_cache_key(user_id, cid) for cid in course_ids]
            cached_vals = await redis.mget(keys)
            for cid, val in zip(course_ids, cached_vals):
                if val is not None:
                    cached_explanations[cid] = val.decode("utf-8") if isinstance(val, bytes) else str(val)
                else:
                    missing_ids.append(cid)
        except Exception as e:
            logger.error(f"Error reading from Redis cache: {e}")
            missing_ids = list(course_ids)

    if missing_ids:
        try:
            user_query = (select(User).where(User.user_id == user_id).options(selectinload(User.tags)))
            user_result = await session.execute(user_query)
            user = user_result.scalar_one_or_none()

            if not user:
                logger.warning(f"User {user_id} not found for explanation generation.")
                user_tags_list = []
                user_description = None
            else:
                user_tags_list = [tag.name for tag in user.tags]
                user_description = user.description

            courses_query = (
                select(Course)
                .where(Course.course_id.in_(missing_ids))
                .options(selectinload(Course.tags))
            )
            courses_result = await session.execute(courses_query)
            courses_db = courses_result.scalars().all()

            has_profile = bool(build_user_profile_text(user_tags_list, user_description))
            if not has_profile or not courses_db:
                for cid in missing_ids:
                    cached_explanations[cid] = "Подходит по вашим интересам (на основе тегов)"
            else:
                courses_for_llm = []
                for course in courses_db:
                    courses_for_llm.append({
                        "course_id": course.course_id,
                        "name": course.name,
                        "tags": [tag.name for tag in course.tags]
                    })

                llm_explainer = LLMExplanation()
                generated_explanations = await llm_explainer.get_explanations(
                    user_tags=user_tags_list,
                    courses_list=courses_for_llm,
                    user_description=user_description,
                )

                explanations_dict = {
                    item.get("course_id"): item.get("explanation")
                    for item in generated_explanations
                    if "course_id" in item and "explanation" in item
                }

                for cid in missing_ids:
                    explanation_text = explanations_dict.get(
                        cid, "Подходит по вашим интересам (на основе тегов)"
                    )
                    cached_explanations[cid] = explanation_text

                    if redis is not None:
                        try:
                            key = _explanation_cache_key(user_id, cid)
                            await redis.set(
                                key,
                                explanation_text,
                                ex=RECOMMENDATIONS_CACHE_TTL_SECONDS,
                            )
                        except Exception as cache_err:
                            logger.error(f"Error writing to Redis cache for course {cid}: {cache_err}")

        except Exception as e:
            logger.error(f"Error generating explanations via LLM: {e}")
            for cid in missing_ids:
                if cid not in cached_explanations:
                    cached_explanations[cid] = "Подходит по вашим интересам (на основе тегов)"

    explanations_list = []
    for cid in course_ids:
        text = cached_explanations.get(cid, "Подходит по вашим интересам (на основе тегов)")
        explanations_list.append(ExplanationItem(course_id=cid, text=text))

    return ExplanationsResponse(user_id=user_id, explanations=explanations_list)
