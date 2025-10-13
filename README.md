# FastAPI Admin Panel

**FastAPI Admin** is a Django-like admin panel for FastAPI built with SQLModel + SQLAlchemy v2.  
It provides automatic model discovery, CRUD operations, and a responsive UI using FastAPI + Jinja2 + HTMX + TailwindCSS.  

---

## Features

- Default User model with fields: `id`, `username`, `email`, `hashed_password`, `is_active`, `is_superuser`
- Ability to customize the User model  
- `createsuperuser` CLI command similar to Django
- Auto-discovery of project models
- Full CRUD for all registered models
- Session-based login
- Responsive UI with TailwindCSS + HTMX + Jinja2

---

## 📦 Installation

### From PyPI

```bash
pip install fastapi-admin
```

Or local development
```
git clone https://github.com/ventuno-21/fastapi-admin.git
cd fastapi-admin
pip install -e .
```

Make sure to install dependencies:  
```
pip install fastapi sqlmodel sqlalchemy jinja2 passlib[bcrypt] typer python-multipart htmx aiofiles
```

🛠 Quick Start
1. Create a superuser  

After installation, create a superuser with the CLI command:  

```
createsuperuser
```

It will prompt for:  

username  

email  

password  

A superuser account will be created in the database.  

2. Create main.py  
```
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_admin.routes_admin import router as admin_router
from fastapi_admin.utils_autodiscover import autodiscover_models
from fastapi_admin.db import init_db
from fastapi_admin.auth import router as auth_router
from fastapi_admin.crud import router as crud_router
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    await init_db()
    yield
    # Shutdown code (if needed)
    # e.g., close connections

app = FastAPI(lifespan=lifespan)

# Mount static files (TailwindCSS)
app.mount("/static", StaticFiles(directory="fastapi_admin/static"), name="static")

# Setup templates
app.state.templates = Jinja2Templates(directory="fastapi_admin/templates")

# Include routers
app.include_router(auth_router)
app.include_router(crud_router)

# Auto-discover models
autodiscover_models(["myproject.models", "shop.models"])
```

Replace ["myproject.models", "shop.models"] with your actual project model paths.  

3. Run the server  
```
uvicorn main:app --reload
```

Admin panel: http://127.0.0.1:8000/admin  

Login page: http://127.0.0.1:8000/login  

📝 Using the Admin Panel  

Login/Logout  
Login: /login  
Logout: /logout  

CRUD for models  
Each registered model has its own list page and create/edit/delete forms.  


⚙️ Managing Models  

To add a new model:  
  
# myproject/models.py  
```
from sqlmodel import SQLModel, Field

class Product(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    price: float
```

Then add the path to autodiscover_models in main.py:  

```
autodiscover_models(["myproject.models"])
```
 
The model will automatically appear in the admin panel.  

🔐 Security  

Session-based login (similar to Django)  
Passwords are hashed using bcrypt  
Only users with is_superuser=True have full access  