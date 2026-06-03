import asyncio
import httpx
from httpx import AsyncClient, Timeout


class StepikClient:
    def __init__(self, client_id: str, client_secret: str):
        self.__base_url = "https://stepik.org"
        self.client = AsyncClient(
            base_url=self.__base_url,
            timeout=Timeout(60.0, connect=15.0)
        )
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

        for attempt in range(4):
            try:
                response = await self.client.request(method, endpoint, **kwargs)

                if response.status_code == 401:
                    await self._authorize()
                    response = await self.client.request(method, endpoint, **kwargs)

                response.raise_for_status()
                return response.json()
            except httpx.RequestError:
                if attempt == 3:
                    raise
                await asyncio.sleep(1.0 + attempt)
            except httpx.HTTPStatusError as e:
                if getattr(e, "response", None) and e.response.status_code in [429, 500, 502, 503, 504]:
                    if attempt == 3:
                        raise
                    await asyncio.sleep(2.0 + attempt)
                else:
                    raise

        raise RuntimeError("Stepik API unavailable")

    async def close(self) -> None:
        await self.client.aclose()
