from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# from . import admin_routes, api_routes
import sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils_autodiscover import autodiscover_models
from admin_routes import router as admin_router
from api_routes import router as api_router
from db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context for startup & shutdown events."""
    # ✅ Startup
    await init_db()
    print("✅ Database initialized")
    yield  # 🔸 Application runs here
    # 🧹 Shutdown
    print("🛑 Application shutting down...")


def create_app(module_paths: list[str] | None = None) -> FastAPI:
    # Create the main FastAPI application instance
    app = FastAPI(title="fastapi-admin"و lifespan=lifespan)

    # Load secret key from environment variable (or fallback to a default)
    # This secret key is used for session encryption
    SECRET = os.getenv("SECRET_KEY", "change-me-in-production")

    # Add session middleware to enable session handling (e.g. user login persistence)
    # This must have a strong secret key in production
    app.add_middleware(SessionMiddleware, secret_key=SECRET)

    # mount static & templates
    # Configure Jinja2 templates (used to render HTML templates)
    templates = Jinja2Templates(directory="fastapi_admin/templates")

    # Serve static files (CSS, JS, images) from the /static path
    app.mount("/static", StaticFiles(directory="fastapi_admin/static"), name="static")

    # autodiscover models specified by the consumer app
    if module_paths:
        autodiscover_models(module_paths)

    # include routers
    app.include_router(admin_router)
    app.include_router(api_router)

    # startup hook: ensure database tables exist
    @app.on_event("startup")
    async def on_startup():
        await init_db()

    @app.get("/")
    async def root(request: Request):
        return templates.TemplateResponse("base.html", {"request": request})

    # Return the configured FastAPI app
    return app


# default app instance (if user mounts directly)
# Create an app instance for running with uvicorn (e.g., `uvicorn my_admin_pkg.main:app`)
app = create_app()
