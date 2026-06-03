from typing import Annotated

from fastapi import Depends

from src.integrations.ml_service.client import MLServiceClient
from src.settings import settings


ml_client = MLServiceClient(base_url=settings.ML_SERVICE_URL)

def get_ml_client() -> MLServiceClient:
    return ml_client

MLClientDep = Annotated[MLServiceClient, Depends(get_ml_client)]
