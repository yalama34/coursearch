import math
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import pandas as pd
import os


class CourseRecommender:

    def __init__(self, csv_path: str = None):
        self.csv_path = csv_path or os.path.join(os.path.dirname(__file__), 'courses.csv')
        self.courses_cache = None

    def load_courses_from_csv(self, file_path: str = None) -> List[Dict[str, Any]]:
        path = file_path or self.csv_path

        try:
            df = pd.read_csv(path)
            courses = []
            for _, row in df.iterrows():
                if isinstance(row['created_at'], str):
                    created_at = datetime.strptime(row['created_at'], '%Y-%m-%d').date()
                else:
                    created_at = row['created_at']

                course = {
                    'id': int(row['id']),
                    'views': int(row['views']),
                    'likes': int(row['likes']),
                    'created_at': created_at
                }
                courses.append(course)

            print(f"Загружено {len(courses)} курсов из {path}")
            self.courses_cache = courses
            return courses

        except FileNotFoundError:
            print(f"Файл {path} не найден")
            return []
        except Exception as e:
            print(f"Ошибка при загрузке CSV: {e}")
            return []

    def get_courses(self) -> List[Dict[str, Any]]:
        if self.courses_cache is not None:
            return self.courses_cache
        return self.load_courses_from_csv()

    def calculate_novelty_score(self, created_at, current_date, half_life=90, scale=1000):
        if isinstance(created_at, datetime):
            created_at = created_at.date()
        age_days = (current_date - created_at).days
        if age_days <= 0:
            return scale
        decay = math.exp(-age_days * 0.693147 / half_life)
        return decay * scale

    def calculate_course_weight(self, course: Dict[str, Any],
                                weights: Dict[str, float],
                                current_date: date,
                                half_life_days: int = 90,
                                scale: int = 1000) -> float:

        views_weight = course['views'] * weights.get('views', 0)
        likes_weight = course['likes'] * weights.get('likes', 0)

        novelty_score = self.calculate_novelty_score(
            course['created_at'],
            current_date,
            half_life_days,
            scale
        )
        novelty_weight = novelty_score * weights.get('novelty', 0)

        total = views_weight + likes_weight + novelty_weight
        return round(total, 4)

    def get_top_n_courses(self,
                          top_n: int = 10,
                          weights: Optional[Dict[str, float]] = None,
                          half_life_days: int = 90,
                          scale: int = 1000,
                          csv_path: str = None) -> Dict[str, Any]:

        if csv_path:
            courses = self.load_courses_from_csv(csv_path)
        else:
            courses = self.get_courses()

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
                course,
                weights,
                current_date,
                half_life_days,
                scale
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
            "course_id": [course['id'] for course in top_courses],
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


def main():
    recommender = CourseRecommender()
    result = recommender.get_top_n_courses(top_n=10)
    print(f"Результат на выходе:{result}")
    print("\n" + "=" * 50)
    print("РЕЗУЛЬТАТ:")
    print("=" * 50)
    print(f"ID курсов: {result['course_id']}")
    print(f"Всего: {result['total']}")
    print(f"Параметры: {result['weights_used']}")


if __name__ == "__main__":
    main()