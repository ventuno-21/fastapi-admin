# Dynamic admin UI routes (session-based authentication).
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND
from .admin_register import get_registered_models
from .db import AsyncSessionLocal
from . import crud
from .security import verify_password
from typing import Any

router = APIRouter()
templates = Jinja2Templates(directory="fastapi_admin/templates")


# helper to fetch current user from session cookie
async def get_current_user(request: Request) -> Any:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    async with AsyncSessionLocal() as db:
        return await crud.get_user(db, int(user_id))


@router.get("/admin/login")
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/admin/login")
async def login_post(
    request: Request, username: str = Form(...), password: str = Form(...)
):
    async with AsyncSessionLocal() as db:
        user = await crud.get_user_by_username_or_email(db, username)
        if not user or not verify_password(password, user.hashed_password):
            return templates.TemplateResponse(
                "login.html", {"request": request, "error": "Invalid credentials"}
            )
        # set session
        request.session["user_id"] = user.id
        return RedirectResponse(url="/admin", status_code=HTTP_302_FOUND)


@router.get("/admin/logout")
async def logout(request: Request):
    request.session.pop("user_id", None)
    return RedirectResponse("/admin/login")


@router.get("/admin")
async def admin_index(request: Request):
    user = await get_current_user(request)
    if not user or not user.is_superuser:
        return RedirectResponse("/admin/login")
    models = get_registered_models()
    # models is a dict name -> class
    return templates.TemplateResponse(
        "admin_index.html", {"request": request, "models": models, "user": user}
    )


# List records for model
@router.get("/admin/model/{model_name}")
async def list_records(request: Request, model_name: str):
    user = await get_current_user(request)
    if not user or not user.is_superuser:
        return RedirectResponse("/admin/login")
    models = get_registered_models()
    model = models.get(model_name)
    if not model:
        return RedirectResponse("/admin")
    async with AsyncSessionLocal() as db:
        records = await crud.list_model(db, model)
    return templates.TemplateResponse(
        "admin_list.html",
        {
            "request": request,
            "model": model,
            "records": records,
            "model_name": model_name,
        },
    )


# Add record (GET form)
@router.get("/admin/model/{model_name}/add")
async def add_record_form(request: Request, model_name: str):
    user = await get_current_user(request)
    if not user or not user.is_superuser:
        return RedirectResponse("/admin/login")
    models = get_registered_models()
    model = models.get(model_name)
    if not model:
        return RedirectResponse("/admin")
    # exclude PK fields from form generation (we assume single 'id' primary key typical case)
    fields = [c.name for c in getattr(model, "__table__").columns if not c.primary_key]
    return templates.TemplateResponse(
        "admin_form.html",
        {
            "request": request,
            "model": model,
            "fields": fields,
            "record": None,
            "model_name": model_name,
        },
    )


# Add record (POST)
@router.post("/admin/model/{model_name}/add")
async def add_record(request: Request, model_name: str):
    user = await get_current_user(request)
    if not user or not user.is_superuser:
        return RedirectResponse("/admin/login")
    models = get_registered_models()
    model = models.get(model_name)
    if not model:
        return RedirectResponse("/admin")
    form = await request.form()
    data = dict(form)
    # simple conversion: empty strings -> None
    for k, v in list(data.items()):
        if v == "":
            data[k] = None
    async with AsyncSessionLocal() as db:
        await crud.create_model_instance(db, model, data)
    return RedirectResponse(f"/admin/model/{model_name}", status_code=HTTP_302_FOUND)


# Edit record form
@router.get("/admin/model/{model_name}/edit/{pk}")
async def edit_record_form(request: Request, model_name: str, pk: int):
    user = await get_current_user(request)
    if not user or not user.is_superuser:
        return RedirectResponse("/admin/login")
    models = get_registered_models()
    model = models.get(model_name)
    if not model:
        return RedirectResponse("/admin")
    # find primary key column name (simple heuristic)
    pk_col = None
    for c in model.__table__.columns:
        if c.primary_key:
            pk_col = c.name
            break
    async with AsyncSessionLocal() as db:
        instance = await crud.get_model_instance(db, model, pk_col, pk)
    fields = [c.name for c in model.__table__.columns if not c.primary_key]
    return templates.TemplateResponse(
        "admin_form.html",
        {
            "request": request,
            "model": model,
            "fields": fields,
            "record": instance,
            "model_name": model_name,
        },
    )


# Edit record POST
@router.post("/admin/model/{model_name}/edit/{pk}")
async def edit_record(request: Request, model_name: str, pk: int):
    user = await get_current_user(request)
    if not user or not user.is_superuser:
        return RedirectResponse("/admin/login")
    models = get_registered_models()
    model = models.get(model_name)
    if not model:
        return RedirectResponse("/admin")
    form = await request.form()
    data = dict(form)
    for k, v in list(data.items()):
        if v == "":
            data[k] = None
    # identify pk col name
    pk_col = None
    for c in model.__table__.columns:
        if c.primary_key:
            pk_col = c.name
            break
    async with AsyncSessionLocal() as db:
        instance = await crud.get_model_instance(db, model, pk_col, pk)
        if not instance:
            return RedirectResponse(
                f"/admin/model/{model_name}", status_code=HTTP_302_FOUND
            )
        await crud.update_model_instance(db, instance, data)
    return RedirectResponse(f"/admin/model/{model_name}", status_code=HTTP_302_FOUND)


# Delete record
@router.get("/admin/model/{model_name}/delete/{pk}")
async def delete_record(request: Request, model_name: str, pk: int):
    user = await get_current_user(request)
    if not user or not user.is_superuser:
        return RedirectResponse("/admin/login")
    models = get_registered_models()
    model = models.get(model_name)
    if not model:
        return RedirectResponse("/admin")
    pk_col = None
    for c in model.__table__.columns:
        if c.primary_key:
            pk_col = c.name
            break
    async with AsyncSessionLocal() as db:
        instance = await crud.get_model_instance(db, model, pk_col, pk)
        if instance:
            await crud.delete_model_instance(db, instance)
    return RedirectResponse(f"/admin/model/{model_name}", status_code=HTTP_302_FOUND)
