from sqlalchemy.ext.asyncio import AsyncSession

from src.providers.registry import PROVIDER_BUILDERS
from src.providers.stepik.provider import StepikProvider
from src.providers.contract import CourseProvider
from src.db.repositories.course_repository import CourseRepository
from src.db.database import async_session_maker
from src.settings import settings


ENABLED_PROVIDERS = [p.strip() for p in settings.ENABLED_PROVIDERS.split(',')]

class CourseSync:
    def __init__(self, session: AsyncSession):
        self._providers_list: list[CourseProvider] = []
        self._db_session: AsyncSession = session

    def add_provider(self, provider: CourseProvider) -> None:
        """Add a provider to the provider list"""
        if not isinstance(provider, CourseProvider):
            raise TypeError("Provider must be of type CourseProvider")
        self._providers_list.append(provider)

    def remove_provider(self, provider: CourseProvider) -> bool:
        """Remove a provider from the provider list"""
        if not isinstance(provider, CourseProvider):
            raise TypeError("Provider must be of type CourseProvider")
        try:
            self._providers_list.remove(provider)
            return True
        except ValueError:
            return False

    def get_provider_names(self) -> list[str]:
        """Return list of provider's names"""
        provider_names = []

        for provider in self._providers_list:
            provider_names.append(provider.source_name)

        return provider_names

    async def sync_courses(self):
        """
        Gets courses and tags from all providers. Saves it to DB
        :return:
        """
        if not self._providers_list:
            return

        repository = CourseRepository(self._db_session)

        for provider in self._providers_list:
            courses = await provider.get_courses()
            if not courses:
                continue
            await repository.upsert_courses(courses)
            tag_names: set[str] = set()
            for course in courses:
                tag_names.update(course.tags)
            if not tag_names:
                continue

            tag_map = await repository.upsert_tags(sorted(tag_names))

            links: list[dict[str, int]] = []
            for course in courses:
                for name in course.tags:
                    tag_id = tag_map.get(name)
                    if tag_id is not None:
                        links.append(
                            {"course_id": course.course_id, "tag_id": tag_id}
                        )

            await repository.link_courses_with_tags(links)

async def run_course_sync() -> None:
    """
    Run course syncing with allowed providers
    :return:
    """
    async with async_session_maker() as session:
        sync = CourseSync(session)

        for provider in ENABLED_PROVIDERS:
            builder = PROVIDER_BUILDERS.get(provider)
            if builder is None:
                continue
            sync.add_provider(builder(settings))

        await sync.sync_courses()
