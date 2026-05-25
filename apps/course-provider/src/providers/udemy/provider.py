from pydemy import Udemy

from src.schemas.course import Course
from src.providers.udemy.mapper import map_udemy_course
from src.providers.udemy.client import UdemyClient


class UdemyProvider:
    source_name = "udemy"

    def __init__(self, client: UdemyClient):
        self.__udemy_client = client

    async def get_courses(self, pages_limit: int | None = None) -> list[Course]:
        all_courses: list[Course] = []
        page = 1
        while True:
            raw_courses = self.__udemy_client.get_courses_from_api(page, pages_limit)

            if not raw_courses:
                break
            for raw_course in raw_courses:
                try:
                    course = map_udemy_course(raw_course)
                    all_courses.append(course)
                except Exception as e:
                    print(f"Failed to map Udemy course: {e}")

            page += 1

            if pages_limit is not None and page > pages_limit:
                break

        return all_courses