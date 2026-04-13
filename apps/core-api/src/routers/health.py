from fastapi import APIRouter
from sqlalchemy import text

from src.db.database import engine


router = APIRouter(tags=["health"], prefix="/health")


@router.get("")
async def health():

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "service": "core-api"
        }

    except Exception:

        return {
            "status": "error"
        }
