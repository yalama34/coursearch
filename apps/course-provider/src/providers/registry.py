from src.providers.stepik.client import StepikClient
from src.providers.stepik.provider import StepikProvider
from src.providers.udemy.client import UdemyClient
from src.providers.udemy.provider import UdemyProvider
from src.settings import Settings


def build_stepik_provider(settings: Settings) -> StepikProvider:
    """
    Creates `StepikClient` object with parameters from `settings`
    :param settings:
    :return: `StepikClient` object
    """
    client = StepikClient(settings.STEPIK_CLIENT_ID, settings.STEPIK_CLIENT_SECRET)
    return StepikProvider(client)

def build_udemy_provider(settings: Settings) -> UdemyProvider:
    """
    Creates `UdemyClient` object with parameters from `settings`
    :param settings:
    :return: `UdemyClient` object
    """
    client = UdemyClient(settings.UDEMY_CLIENT_ID, settings.UDEMY_CLIENT_SECRET)
    return UdemyProvider(client)


PROVIDER_BUILDERS = {
    "stepik": build_stepik_provider,
    "udemy": build_udemy_provider
}
