from pydemy import UdemyClient as Client
from pydemy.models import CourseFilter, Course as UdemyCourse


class UdemyClient:
    def __init__(self, client_id: str, client_secret: str):
        self.__client = Client(client_id=client_id, client_secret=client_secret)
        self.__client._UdemyClient__base_url = self.__client.base_url
        self.__client._UdemyClient__auth = self.__client.auth
        self.__client._UdemyClient__timeout = self.__client.timeout

    def get_courses_from_api(self, page: int = 1, page_size: int = 100) -> list[UdemyCourse]:
        course_filter = CourseFilter(page=page, page_size=page_size)
        response = self.__client.get_courses(filters=course_filter)

        return response
