from pydemy import Udemy


class UdemyClient:
    def __init__(self, client_id: str, client_secret: str):
        self.__client = Udemy(client_id=client_id, сlient_secret=client_secret)

    def get_courses_from_api(self, page: int = 1, page_size: int = 100) -> list[dict]:
        response = self.__client.courses(page=page, page_size=page_size)

        return response.get("results", [])
