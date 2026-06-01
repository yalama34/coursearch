import logging
from sqlalchemy.ext.asyncio import AsyncSession

from src.providers.registry import PROVIDER_BUILDERS
from src.providers.stepik.provider import StepikProvider
from src.providers.contract import CourseProvider
from src.db.repositories.course_repository import CourseRepository
from src.db.database import async_session_maker
from src.quality.validator import filter_valid_courses
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
            logger.info("No providers configured for sync.")
            return

        logger.info(f"Starting sync_courses for {len(self._providers_list)} providers with pages_limit={pages_limit}")
        repository = CourseRepository(self._db_session)

        for provider in self._providers_list:
            logger.info(f"Syncing from provider: {provider.source_name if hasattr(provider, 'source_name') else provider}")
            courses = await provider.get_courses(pages_limit=pages_limit)
            courses = filter_valid_courses(courses)
            if not courses:
                logger.info(f"No courses returned from provider {provider.source_name if hasattr(provider, 'source_name') else provider}")
                continue
                
            logger.info(f"Upserting {len(courses)} courses to DB...")
            await repository.upsert_courses(courses)
            
            tag_names: set[str] = set()
            for course in courses:
                tag_names.update(course.tags)
                
            if not tag_names:
                logger.info("No tags found in the synced courses.")
                continue

            logger.info(f"Upserting {len(tag_names)} tags to DB...")
            tag_map = await repository.upsert_tags(sorted(tag_names))

            links: list[dict[str, int]] = []
            for course in courses:
                for name in course.tags:
                    tag_id = tag_map.get(name)
                    if tag_id is not None:
                        links.append(
                            {"course_id": course.course_id, "tag_id": tag_id}
                        )

            logger.info(f"Linking {len(links)} courses with tags in DB...")
            await repository.link_courses_with_tags(links)
            logger.info(f"Finished sync for provider: {provider.source_name if hasattr(provider, 'source_name') else provider}")

        logger.info("sync_courses completed successfully.")

async def run_course_sync(pages_limit: int | None = None) -> None:
    """
    Run course syncing with allowed providers
    :return:
    """
    logger.info(f"run_course_sync triggered. ENABLED_PROVIDERS: {ENABLED_PROVIDERS}")
    try:
        async with async_session_maker() as session:
            sync = CourseSync(session)

            for provider in ENABLED_PROVIDERS:
                builder = PROVIDER_BUILDERS.get(provider)
                if builder is None:
                    logger.info(f"Builder for provider '{provider}' not found.")
                    continue
                sync.add_provider(builder(settings))

            await sync.sync_courses(pages_limit=pages_limit)
    except Exception as e:
        logger.info(f"Error during run_course_sync: {e}")
        raise
