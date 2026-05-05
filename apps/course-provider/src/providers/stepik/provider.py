from src.providers.stepik.client import StepikClient
from src.schemas.course import Course


class StepikProvider:
    def __init__(self, client: StepikClient):
        self.client = client
        self.source_name = "stepik"

    async def _fetch_tags(self, tag_ids: set[int]) -> dict[int, str]:
        params = [("ids[]", tag_id) for tag_id in tag_ids]
        data = await self.client.send_request("GET", "/api/tags", params=params)

        return {tag["id"]: tag["title"] for tag in data.get("tags", [])}

    async def get_courses(self) -> list[Course]:
        all_courses = []
        page = 1
        has_next = True

        while has_next:
            data = await self.client.send_request("GET", "/api/courses", params={"page": page})
            raw_courses = data.get("courses", [])

            tag_ids_from_request = set()
            for raw_course in raw_courses:
                tag_ids_from_request.update(raw_course.get("tags", []))

            tags_mapped = await self._fetch_tags(tag_ids_from_request)

            for raw_course in raw_courses:
                course_tags = [
                    tags_mapped[tag_id]
                    for tag_id in raw_course.get("tags") or []
                    if tag_id in tags_mapped
                ]

                course_obj = Course(
                    course_id=raw_course.get("id"),
                    name=raw_course.get("title"),
                    description=raw_course.get("summary") or raw_course.get("description"),
                    difficulty=raw_course.get("difficulty"),
                    link=raw_course.get("canonical_url") or f"https://stepik.org/course/{raw_course['id']}/",
                    source=self.source_name,
                    tags=course_tags,
                )

                all_courses.append(course_obj)
            has_next = data.get("meta", {}).get("has_next", False)
            page += 1

        await self.client.close()
        return all_courses
