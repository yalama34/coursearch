from src.providers.stepik.client import StepikClient
from src.providers.stepik.provider import StepikProvider
from src.settings import Settings

def build_stepik_provider(settings: Settings) -> StepikProvider:
    """
    Creates `StepikClient` object with parameters from `settings`
    :param settings:
    :return: `StepikClient` object
    """
    client = StepikClient(settings.STEPIK_CLIENT_ID, settings.STEPIK_CLIENT_SECRET)
    return StepikProvider(client)

PROVIDER_BUILDERS = {
    "stepik": build_stepik_provider
}
