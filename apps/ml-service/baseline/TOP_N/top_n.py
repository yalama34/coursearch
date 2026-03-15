import math
from datetime import datetime, date
from typing import List, Dict, Any, Optional

class CourseRecommender:

    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.connection = None

    def get_courses_from_db(self) -> List[Dict[str, Any]]:
    #заглушка тут должна быть
        courses = [
            {'id': 1, 'views': 15000, 'likes': 1200, 'created_at': date(2025, 1, 15)},
            {'id': 2, 'views': 5000, 'likes': 350, 'created_at': date(2025, 2, 20)},
            {'id': 3, 'views': 200000, 'likes': 15000, 'created_at': date(2024, 11, 5)},
        ]
        return courses

    def calculate_novelty_score(self, created_at, current_date, half_life=90, scale=1000):
        if isinstance(created_at, datetime):
            created_at = created_at.date()
        age_days = (current_date - created_at).days
        if age_days <= 0:
            return scale
        # Экспоненциальное затухание: exp(-age * ln(2) / half_life)
        # ln(2) ~ 0.693147
        decay = math.exp(-age_days * 0.693147 / half_life)
        return decay * scale

    def calculate_course_weight(self, course: Dict[str, Any],
                                weights: Dict[str, float],
                                current_date: date,
                                half_life_days: int = 90) -> float:

        views_weight = course['views'] * weights.get('views', 0)

        likes_weight = course['likes'] * weights.get('likes', 0)

        novelty_score = self.calculate_novelty_score(
            course['created_at'],
            current_date,
            half_life_days
        )
        novelty_weight = novelty_score * weights.get('novelty', 0)

        # Суммируем
        total = views_weight + likes_weight + novelty_weight
        return round(total, 4)

    def get_top_n_courses(self,
                          top_n: int = 10,
                          weights: Optional[Dict[str, float]] = None,
                          half_life_days: int = 90) -> List[int]:

        if weights is None:
            weights = {
                'views': 0.2,
                'likes': 0.5,
                'novelty': 0.3
            }

        total_weight_sum = sum(weights.values())
        print(f"Используемые веса: {weights}, сумма = {total_weight_sum}")

        courses = self.get_courses_from_db()

        current_date = date.today()

        courses_with_weights = []
        for course in courses:
            weight = self.calculate_course_weight(
                course,
                weights,
                current_date,
                half_life_days
            )

            courses_with_weights.append({
                'id': course['id'],
                'weight': weight,
                'views': course['views'],
                'likes': course['likes'],
                'created_at': course['created_at']
            })

        # Сортируем по убыванию веса
        sorted_courses = sorted(
            courses_with_weights,
            key=lambda x: x['weight'],
            reverse=True
        )

        top_courses = sorted_courses[:top_n]

        print(f"\nТоп-{top_n} курсов:")
        for i, course in enumerate(top_courses, 1):
            print(f"{i}. Курс {course['id']}: вес = {course['weight']} "
                  f"(просмотров: {course['views']}, лайков: {course['likes']}, "
                  f"создан: {course['created_at']})")

        return [course['id'] for course in top_courses]

def main():

    db_config = {
        'host': 'localhost',
        'database': 'courses_db',
        'user': 'postgres',
        'password': 'password'
    }

    recommender = CourseRecommender(db_config)

    top_courses = recommender.get_top_n_courses(top_n=5)
    print(f"Результат (ID курсов): {top_courses}")

if __name__ == "__main__":
    main()