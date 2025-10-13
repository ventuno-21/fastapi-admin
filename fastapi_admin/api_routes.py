# Minimal JSON endpoints for models (optional). You can extend/add auth for API.
from fastapi import APIRouter
from fastapi_admin.admin_register import get_registered_models
from fastapi_admin.db import AsyncSessionLocal
from fastapi_admin import crud

router = APIRouter(prefix="/api")


@router.get("/models")
async def list_models():
    """
    Return registered models.
    """
    models = get_registered_models()
    return {"models": list(models.keys())}


@router.get("/models/{model_name}")
async def list_model_records(model_name: str):
    models = get_registered_models()
    model = models.get(model_name)
    if not model:
        return {"error": "model not found"}
    async with AsyncSessionLocal() as db:
        records = await crud.list_model(db, model)
    return {"count": len(records), "items": [r.__dict__ for r in records]}
