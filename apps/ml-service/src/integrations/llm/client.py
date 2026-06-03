import os
import logging

from openai import AsyncOpenAI


logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.__base_url = os.getenv("LLM_BASE_URL")
        self.__api_key = os.getenv("LLM_API_KEY")
        self.__client = AsyncOpenAI(
            base_url=self.__base_url,
            api_key=self.__api_key,
            timeout=120.0
        )

    async def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate response from given system and user prompts
        :param system_prompt:
        :param user_prompt:
        :return:
        """
        try:
            logging.info("[LLM] Generating response")
            response = await self.__client.chat.completions.create(
                model="Qwen3.5-122B-A10B",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
            )
            logging.info("[LLM] Generated response successfully")
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {e}")
