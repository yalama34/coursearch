from datetime import date
from top_n import CourseRecommender


def interactive_weight_input():

    recommender = CourseRecommender()

    print("ИНТЕРАКТИВНЫЙ ПОДБОР ВЕСОВ")
    print("Введите параметры (для выхода введите 'q')")

    while True:
        try:
            print("\n" + "-" * 40)

            views = input("Вес просмотров (0-1): ").strip()
            if views.lower() == 'q':
                break

            likes = input("Вес лайков (0-1): ").strip()
            if likes.lower() == 'q':
                break

            novelty = input("Вес новизны (0-1): ").strip()
            if novelty.lower() == 'q':
                break

            half_life = input("Период полураспада (дней, Enter=90): ").strip()
            if half_life.lower() == 'q':
                break

            scale = input("Множитель новизны (scale, Enter=1000): ").strip()
            if scale.lower() == 'q':
                break

            weights = {
                'views': float(views),
                'likes': float(likes),
                'novelty': float(novelty)
            }

            half_life = int(half_life) if half_life else 90
            scale = int(scale) if scale else 1000

            total = sum(weights.values())
            if abs(total - 1.0) > 0.01:
                print(f"Предупреждение: сумма весов = {total:.2f}, рекомендуется 1.0")

            print("\nРезультат:")
            top_courses = recommender.get_top_n_courses(
                top_n=5,
                weights=weights,
                half_life_days=half_life,
                scale=scale
            )

            print(f"\nID курсов: {top_courses['course_id']}")

            print("\nДетализация:")
            courses = recommender.get_courses()
            current_date = date.today()

            for course in courses:
                if course['id'] in top_courses['course_id']:
                    novelty = recommender.calculate_novelty_score(
                        course['created_at'],
                        current_date,
                        half_life,
                        scale
                    )
                    print(f"Курс {course['id']}: "
                          f"просмотры={course['views']}, "
                          f"лайки={course['likes']}, "
                          f"новизна={novelty:.1f}")

        except ValueError as e:
            print(f"Ошибка ввода: {e}")
        except KeyboardInterrupt:
            print("\nВыход")
            break


if __name__ == "__main__":
    interactive_weight_input()