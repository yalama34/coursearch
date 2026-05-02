from httpx import AsyncClient


class StepikClient:
    def __init__(self, client_id: str, client_secret: str):
        self.__base_url = "https://stepik.org"
        self.client = AsyncClient(base_url=self.__base_url)
        self.__client_id = client_id
        self.__client_secret = client_secret
        self._token: str | None = None

    async def _authorize(self):
        response = await self.client.post(
            '/oauth2/token/',
            data={'grant_type': 'client_credentials'},
            auth=(self.__client_id, self.__client_secret)
        )

        response.raise_for_status()
        self._token = response.json()["access_token"]

        self.client.headers.update({
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json"
        })

    async def send_request(self, method: str, endpoint: str, **kwargs) -> dict[str, int | str]:
        if not self._token:
            await self._authorize()

        response = await self.client.request(method, endpoint, **kwargs)

        if response.status_code == 401:
            await self._authorize()
            response = await self.client.request(method, endpoint, **kwargs)

        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        await self.client.aclose()
