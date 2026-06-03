import math
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.db.models import Course, Action
from src.domain.enum.action_type import ActionType
from src.schemas.recommendations import RecommendationItem, RecommendationExplanation
from src.domain.recommendation.pipeline_order import StageName


logger = logging.getLogger(__name__)

class TopNStage:
    def __init__(self, db_session: AsyncSession = None):
        """
        :param db_session: Async SQLAlchemy session (optional)
        """
        self.db_session = db_session

    @property
    def stage_name(self) -> str:
        return StageName.TOP_N

    async def process(
            self,
            user_id: int,
            candidates: list[RecommendationItem],
            limit: int = 10
    ) -> list[RecommendationItem]:
        """
        If candidates is empty: get all courses from db and returns top-limit by their popularity
        If candidates is not empty: sorts candidates by popularity
        :param user_id:
        :param candidates:
        :param limit:
        :return:
        """

        candidate_ids = [c.item_id for c in candidates] if candidates else None

        logger.info(f"[{self.stage_name}] Starting TopNStage for user_id={user_id}. Candidates count: {len(candidates) if candidates else 0}, limit={limit}")

        top_data = await self.get_top_n_courses(
            top_n=limit,
            candidate_ids=candidate_ids
        )

        course_ids = top_data.get("course_ids", [])
        weights_map = top_data.get("weights_map", {})

        logger.debug(f"[{self.stage_name}] Received {len(course_ids)} top courses from db")

        result_candidates = []

        for cid in course_ids:
            existing_candidate = next((c for c in candidates if c.item_id == cid), None)

            if existing_candidate:
                result_candidates.append(existing_candidate)
            else:
                weight = weights_map.get(cid, 0.0)
                explanation = RecommendationExplanation(
                    text="Популярный курс",
                    confidence=weight
                )
                item = RecommendationItem(item_id=cid, explanation=explanation)
                result_candidates.append(item)

        logger.info(f"[{self.stage_name}] Finished TopNStage for user_id={user_id}. Returned {len(result_candidates)} items.")

        return result_candidates

    async def get_courses(self) -> List[Dict[str, Any]]:
        """
        Loads data from db
        """
        if self.db_session is None:
            raise ValueError("Database session is not configured")

        try:
            query = (
                select(
                    Course.course_id,
                    func.count(
                        Action.action_id
                    ).filter(Action.action_type == ActionType.VIEW).label('views'),
                    func.count(
                        Action.action_id
                    ).filter(Action.action_type == ActionType.LIKE).label('likes')
                )
                .outerjoin(Action, Course.course_id == Action.course_id)
                .group_by(Course.course_id)
                .order_by(Course.course_id)
            )

            result = await self.db_session.execute(query)
            rows = result.all()

            courses = []
            for row in rows:
                course = {
                    'id': row.course_id,
                    'views': row.views or 0,
                    'likes': row.likes or 0,
                    'created_at': date.today()
                }
                courses.append(course)

            return courses

        except Exception as e:
            raise RuntimeError(f"Failed to load courses from the database: {e}")

    def calculate_novelty_score(self,
                                created_at: date,
                                current_date: date,
                                half_life: int = 90,
                                scale: int = 1000) -> float:
        """
        Counts the novelty score between created_at and current_date
        :param created_at:
        :param current_date:
        :param half_life:
        :param scale:
        :return:
        """
        if isinstance(created_at, datetime):
            created_at = created_at.date()
        age_days = (current_date - created_at).days
        if age_days <= 0:
            return scale
        decay = math.exp(-age_days * 0.693147 / half_life)
        return decay * scale

    def calculate_course_weight(self,
                                course: Dict[str, Any],
                                weights: Dict[str, float],
                                current_date: date,
                                half_life_days: int = 90,
                                scale: int = 1000) -> float:
        """
        Calculates the weight of a course
        :param course:
        :param weights:
        :param current_date:
        :param half_life_days:
        :param scale:
        :return:
        """
        views_weight = course['views'] * weights.get('views', 0)
        likes_weight = course['likes'] * weights.get('likes', 0)
        novelty_score = self.calculate_novelty_score(
            course['created_at'], current_date, half_life_days, scale
        )
        novelty_weight = novelty_score * weights.get('novelty', 0)
        total = views_weight + likes_weight + novelty_weight
        return round(total, 4)

    async def get_top_n_courses(self,
                                top_n: int = 10,
                                candidate_ids: Optional[List[int]] = None,
                                weights: Optional[Dict[str, float]] = None,
                                half_life_days: int = 90,
                                scale: int = 1000) -> Dict[str, Any]:

        courses = await self.get_courses()

        if not courses:
            return {
                "course_ids": [],
                "weights_map": {},
                "total": 0,
                "error": "No data available for recommendations"
            }

        if candidate_ids is not None:
            candidate_set = set(candidate_ids)
            courses = [c for c in courses if c['id'] in candidate_set]

        if weights is None:
            weights = {
                'views': 0.2,
                'likes': 0.5,
                'novelty': 0.3
            }

        current_date = date.today()

        courses_with_weights = []
        weights_map = {}

        for course in courses:
            weight = self.calculate_course_weight(
                course, weights, current_date, half_life_days, scale
            )
            courses_with_weights.append({
                'id': course['id'],
                'weight': weight,
                'views': course['views'],
                'likes': course['likes'],
                'created_at': course['created_at']
            })
            weights_map[course['id']] = weight

        sorted_courses = sorted(
            courses_with_weights,
            key=lambda x: x['weight'],
            reverse=True
        )
        top_courses = sorted_courses[:top_n]

        result = {
            "course_ids": [course['id'] for course in top_courses],
            "weights_map": weights_map,
            "total": len(top_courses),
            "weights_used": weights,
            "half_life_days": half_life_days,
            "scale": scale,
            "timestamp": current_date.isoformat()
        }

        return result