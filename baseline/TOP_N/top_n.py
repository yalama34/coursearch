import math
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import asyncio
from sqlalchemy import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from db.models import Course, Action
from db.database import async_session_maker


class CourseRecommender:
    """
    Рекомендательная система на основе популярности и новизны курсов.

    Принцип работы:
    - Загружает данные курсов из БД (id, просмотры, лайки, дата создания)
    - Для каждого курса вычисляет общий вес как взвешенную сумму:
        weight = views * w_views + likes * w_likes + novelty_score * w_novelty
      где novelty_score = scale * exp(-age_days * ln2 / half_life)
    - Сортирует курсы по убыванию веса и возвращает top-N идентификаторов
    """

    def __init__(self, db_session: AsyncSession = None):
        """
        Args:
            db_session: асинхронная сессия SQLAlchemy (опционально)
        """
        self.db_session = db_session
        self.courses_cache = None

    async def load_courses_from_db(self) -> List[Dict[str, Any]]:
        """
        Загружает данные курсов из базы данных.

        Возвращает список словарей с ключами:
        - id (int): идентификатор курса
        - views (int): количество просмотров
        - likes (int): количество лайков
        - created_at (date): дата создания

        В случае ошибки выбрасывает исключение.
        """
        if self.db_session is None:
            raise ValueError("Не передана сессия базы данных")

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

            print(f"Загружено {len(courses)} курсов из базы данных")
            self.courses_cache = courses
            return courses

        except Exception as e:
            raise RuntimeError(f"Ошибка при загрузке данных из БД: {e}")

    async def get_courses(self) -> List[Dict[str, Any]]:
        """
        Получает курсы (из кэша или загружает заново)
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
        Вычисляет оценку новизны курса
        novelty = scale * exp(-age * ln(2) / half_life)
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
        Returns:
            Dict с ключами:
            - course_ids: список ID курсов
            - total: количество
            - weights_used: использованные веса
            - half_life_days: период полураспада
            - scale: множитель новизны
            - timestamp: дата расчета
        """
        courses = await self.get_courses()

        if not courses:
            return {
                "course_ids": [],
                "total": 0,
                "error": "Нет данных для рекомендаций"
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

        print(f"\nТоп-{top_n} курсов:")
        for i, course in enumerate(top_courses, 1):
            print(f"{i}. Курс {course['id']}: вес = {course['weight']} "
                  f"(просмотров: {course['views']}, лайков: {course['likes']}, "
                  f"создан: {course['created_at']})")

        return result