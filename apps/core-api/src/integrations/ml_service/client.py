import asyncio

import httpx

from src.integrations.ml_service.schemas import ExplanationsResponse, RecommendationResponse

class MLServiceClient:
    def __init__(self, base_url: str = "http://ml-service:8001"):
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=httpx.Timeout(timeout=120.0, connect=5.0),
        )

    async def _request_with_retry(
            self,
            method: str,
            url: str,
            **kwargs
    ) -> dict:
        """
        Base method for making requests to ML service
        """
        for attempt in range(3):
            try:
                response = await self.client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()

            except httpx.RequestError:
                if attempt == 2:
                    raise
                await asyncio.sleep(0.5)

            except httpx.HTTPStatusError as e:
                if 400 <= e.response.status_code < 500:
                    raise
                if attempt == 2:
                    raise
                await asyncio.sleep(0.5)

        raise RuntimeError("ML service unavailable")

    async def get(self, path: str, params: dict | None = None) -> dict:
        """
        Make a GET request to ML service
        """
        return await self._request_with_retry("GET", path, params=params)

    async def post(self, path: str, json: dict | None = None) -> dict:
        """
        Make a POST request to ML service
        """
        return await self._request_with_retry("POST", path, json=json)

    async def close(self):
        """
        Close the connection to the ML service
        """
        await self.client.aclose()


    async def get_recommendations(
            self,
            user_id: int,
            limit: int = 10,
            force: bool = False,
    ) -> RecommendationResponse:
        """
        Get recommendations for a user by user ID
        Return number of limit recommendations (10 as default)
        Make GET request to ML service
        """
        data = await self.get(
            path="/recommendations",
            params={
                "user_id": user_id,
                "limit": limit,
                "force": force,
            },
        )
        return RecommendationResponse.model_validate(data)

    async def get_explanations(
            self,
            user_id: int,
            course_ids: list[int],
    ) -> ExplanationsResponse:
        data = await self.get(
            path="/recommendations/explanations",
            params={
                "user_id": user_id,
                "course_ids": ",".join(str(cid) for cid in course_ids),
            },
        )
        return ExplanationsResponse.model_validate(data)
