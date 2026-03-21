import math
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Union
import pandas as pd
import os


class CourseRecommender:
    """
        Рекомендательная система на основе популярности и новизны курсов.

        Принцип работы:
        - Загружает данные курсов из CSV (id, views, likes, created_at).
        - Для каждого курса вычисляет общий вес как взвешенную сумму:
            weight = views * w_views + likes * w_likes + novelty_score * w_novelty
          где novelty_score = scale * exp(-age_days * ln2 / half_life).
        - Сортирует курсы по убыванию веса и возвращает top-N идентификаторов.

        Параметры:
            csv_path (str, optional): путь к CSV-файлу. По умолчанию ищется в директории скрипта.
        """
    def __init__(self, csv_path: str = None):
        self.csv_path = csv_path or os.path.join(os.path.dirname(__file__), 'courses.csv')
        self.courses_cache = None

    def load_courses_from_csv(self, file_path: str = None) -> List[Dict[str, Any]]:
        """
            Загружает данные курсов из CSV-файла.

            Ожидаемые колонки: id, views, likes, created_at (формат YYYY-MM-DD).
            Возвращает список словарей с ключами id, views, likes, created_at (date).
            При отсутствии файла возвращает пустой список.
            """
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
            raise FileNotFoundError(f"CSV файл не найден: {path}")
        except Exception as e:
            raise RuntimeError(f"Ошибка при загрузке CSV: {e}")
        except pd.errors.EmptyDataError:
            raise ValueError(f"CSV файл пуст: {path}")

    def get_courses(self) -> List[Dict[str, Any]]:
        if self.courses_cache is not None:
            return self.courses_cache
        return self.load_courses_from_csv()

    def calculate_novelty_score(self,
                                created_at: Union[date, datetime],
                                current_date: date,
                                half_life: int = 90,
                                scale: int = 1000) -> float:
        """
            Вычисляет оценку новизны курса.

            Оценка вычисляется по формуле экспоненциального затухания:
                novelty = scale * exp(-age * ln(2) / half_life)
            где age = (current_date - created_at).days.

            Args:
                created_at: дата создания курса (date или datetime).
                current_date: текущая дата (date).
                half_life: период полураспада в днях (по умолчанию 90).
                scale: множитель для приведения к масштабу других признаков (по умолчанию 1000).

            Returns:
                float: оценка новизны (убывает с возрастом курса).
            """
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