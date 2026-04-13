from ..integrations.ml_service.client import MLServiceClient
from ..settings import settings

ml_client = MLServiceClient(base_url=settings.ML_SERVICE_URL)


def get_ml_client() -> MLServiceClient:
    return ml_client
