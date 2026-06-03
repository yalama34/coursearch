import json

from src.integrations.llm.client import LLMClient
from src.integrations.llm.prompts.expl_system import EXPLANATION_SYSTEM_PROMPT


class LLMExplanation:
    def __init__(self) -> None:
        self.__client = LLMClient()

    async def get_explanations(
        self,
        user_tags: list[str],
        courses_list: list[dict[str, int | str]],
        user_description: str | None = None,
    ) -> list[dict[str, int | str]]:
        """
        Gets recommendations explanations using LLM for given user and course tags
        :param user_tags:
        :param courses_list:
        :param user_description:
        :return:
        """
        user_tags_str = ", ".join(user_tags) if user_tags else "не указаны"
        about_text = user_description.strip() if user_description and user_description.strip() else "не указано"

        courses_text = ""
        for course in courses_list:
            course_id = course.get("course_id")
            name = course.get("name", "Без названия")
            tags = ", ".join(course.get("tags", []))
            courses_text += f"- ID: {course_id} | Название: {name} | Теги курса: {tags}\n"
        user_prompt: str = f"""
        ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ:
        Интересы (теги): {user_tags_str}
        О себе: {about_text}

        КУРСЫ, ДЛЯ КОТОРЫХ НУЖНО НАПИСАТЬ ОБЪЯСНЕНИЯ:
        {courses_text}

        Задание: Напиши объяснение для каждого курса из списка выше. Верни результат строго в формате JSON-массива.
        """

        try:
            response_text = await self.__client.generate_response(
                system_prompt=EXPLANATION_SYSTEM_PROMPT,
                user_prompt=user_prompt
            )

            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            elif cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]

            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]

            cleaned_text = cleaned_text.strip()

            explanations_data = json.loads(cleaned_text)

            if not isinstance(explanations_data, list):
                print("LLM returned JSON, but it is not a list.")
                return []

            return explanations_data
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON from LLM response: {e}")
            return []
        except Exception as e:
            print(f"Error during LLM explanation generation: {e}")
            return []
