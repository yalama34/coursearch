import logging
from sqlalchemy.ext.asyncio import AsyncSession

from src.providers.registry import PROVIDER_BUILDERS
from src.providers.stepik.provider import StepikProvider
from src.providers.contract import CourseProvider
from src.db.repositories.course_repository import CourseRepository
from src.db.database import async_session_maker
from src.settings import settings

logger = logging.getLogger(__name__)

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

    async def sync_courses(self, pages_limit: int | None = None):
        """
        Gets courses and tags from all providers. Saves it to DB
        :return:
        """
        if not self._providers_list:
            print("No providers configured for sync.", flush=True)
            return

        print(f"Starting sync_courses for {len(self._providers_list)} providers with pages_limit={pages_limit}", flush=True)
        repository = CourseRepository(self._db_session)

        for provider in self._providers_list:
            print(f"Syncing from provider: {provider.source_name if hasattr(provider, 'source_name') else provider}", flush=True)
            courses = await provider.get_courses(pages_limit=pages_limit)
            if not courses:
                print(f"No courses returned from provider {provider.source_name if hasattr(provider, 'source_name') else provider}", flush=True)
                continue
                
            print(f"Upserting {len(courses)} courses to DB...", flush=True)
            await repository.upsert_courses(courses)
            
            tag_names: set[str] = set()
            for course in courses:
                tag_names.update(course.tags)
                
            if not tag_names:
                print("No tags found in the synced courses.", flush=True)
                continue

            print(f"Upserting {len(tag_names)} tags to DB...", flush=True)
            tag_map = await repository.upsert_tags(sorted(tag_names))

            links: list[dict[str, int]] = []
            for course in courses:
                for name in course.tags:
                    tag_id = tag_map.get(name)
                    if tag_id is not None:
                        links.append(
                            {"course_id": course.course_id, "tag_id": tag_id}
                        )

            print(f"Linking {len(links)} courses with tags in DB...", flush=True)
            await repository.link_courses_with_tags(links)
            print(f"Finished sync for provider: {provider.source_name if hasattr(provider, 'source_name') else provider}", flush=True)

        print("sync_courses completed successfully.", flush=True)

async def run_course_sync(pages_limit: int | None = None) -> None:
    """
    Run course syncing with allowed providers
    :return:
    """
    print(f"run_course_sync triggered. ENABLED_PROVIDERS: {ENABLED_PROVIDERS}", flush=True)
    try:
        async with async_session_maker() as session:
            sync = CourseSync(session)

            for provider in ENABLED_PROVIDERS:
                builder = PROVIDER_BUILDERS.get(provider)
                if builder is None:
                    print(f"Builder for provider '{provider}' not found.", flush=True)
                    continue
                sync.add_provider(builder(settings))

            await sync.sync_courses(pages_limit=pages_limit)
    except Exception as e:
        print(f"Error during run_course_sync: {e}", flush=True)
        raise
