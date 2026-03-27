import math


from datetime import datetime, date
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func


from ..db.models import Course, Action


class CourseTopNPipeline:
    """
    Popularity and novelty-based course recommendations.

    Behaviour:
    - Loads course aggregates from the DB (id, views, likes, created_at).
    - Computes a scalar weight per course as a weighted sum:
        weight = views * w_views + likes * w_likes + novelty_score * w_novelty
      where novelty_score = scale * exp(-age_days * ln(2) / half_life).
    - Sorts by descending weight and returns the top-N course ids.
    """

    def __init__(self, db_session: AsyncSession = None):
        """
        :param db_session: Async SQLAlchemy session (optional).
        """
        self.db_session = db_session
        self.courses_cache = None

    async def load_courses_from_db(self) -> List[Dict[str, Any]]:
        """
        Load per-course aggregates from the database.

        :return: List of dicts with keys:
            - id (int): course id
            - views (int): view count
            - likes (int): like count
            - created_at (date): creation date

        :raises RuntimeError: if the query fails.
        :raises ValueError: if no DB session was configured.
        """
        if self.db_session is None:
            raise ValueError("Database session is not configured")

        try:
            query = (
                select(
                    Course.course_id,
                    Course.created_at,
                    func.count(
                        Action.action_id
                    ).filter(Action.action_type == 'view').label('views'),
                    func.count(
                        Action.action_id
                    ).filter(Action.action_type == 'like').label('likes')
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
                    'created_at': row.created_at.date() if row.created_at else date.today()
                }
                courses.append(course)

            self.courses_cache = courses
            return courses

        except Exception as e:
            raise RuntimeError(f"Failed to load courses from the database: {e}")

    async def get_courses(self) -> List[Dict[str, Any]]:
        """
        Return cached courses if present, otherwise load from the database.
        """
        if self.courses_cache is not None:
            return self.courses_cache
        return await self.load_courses_from_db()

    def calculate_novelty_score(self,
                                created_at: date,
                                current_date: date,
                                half_life: int = 90,
                                scale: int = 1000) -> float:
        """
        Novelty score for a course by age (exponential decay).
        novelty = scale * exp(-age_days * ln(2) / half_life)
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
                                weights: Optional[Dict[str, float]] = None,
                                half_life_days: int = 90,
                                scale: int = 1000) -> Dict[str, Any]:
        """
        :return: Dict with keys:
            - course_ids: ordered list of course ids (highest weight first)
            - total: number of ids returned
            - weights_used: weight map used for scoring
            - half_life_days: novelty half-life in days
            - scale: novelty scale factor
            - timestamp: computation date (ISO date string)
        """
        courses = await self.get_courses()

        if not courses:
            return {
                "course_ids": [],
                "total": 0,
                "error": "No data available for recommendations"
            }

        if weights is None:
            weights = {
                'views': 0.2,
                'likes': 0.5,
                'novelty': 0.3
            }

        current_date = date.today()

        courses_with_weights = []
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

        sorted_courses = sorted(
            courses_with_weights,
            key=lambda x: x['weight'],
            reverse=True
        )
        top_courses = sorted_courses[:top_n]

        result = {
            "course_ids": [course['id'] for course in top_courses],
            "total": len(top_courses),
            "weights_used": weights,
            "half_life_days": half_life_days,
            "scale": scale,
            "timestamp": current_date.isoformat()
        }

        return result