import importlib
import inspect
import pkgutil
from typing import List
from sqlmodel import SQLModel
from .admin_register import register_model


import importlib
import inspect
import pkgutil
from typing import List, Type

from sqlmodel import SQLModel
from sqlalchemy.orm import DeclarativeMeta


# my_admin_pkg/utils_autodiscover.py
import importlib
import inspect
import pkgutil
from typing import List, Type

from sqlmodel import SQLModel
from .admin_register import register_model


def is_sqlalchemy_model(obj: Type) -> bool:
    """
    Check whether the given object is a SQLAlchemy or SQLModel model class.
    This function supports both SQLAlchemy v1 and v2.

    It recognizes models created with:
      - SQLModel (used with FastAPI)
      - SQLAlchemy declarative_base() (v1)
      - SQLAlchemy DeclarativeBase / registry() (v2)
    """
    # --- Case 1: SQLModel-based models (FastAPI style) ---
    if issubclass(obj, SQLModel) and getattr(obj, "__table__", None):
        return True

    # --- Case 2: SQLAlchemy models ---
    # These usually have:
    #   __table__ or __tablename__ (table definition)
    #   __mapper__ (SQLAlchemy ORM mapper)
    #   registry (in SQLAlchemy v2)
    has_table = (
        getattr(obj, "__table__", None) is not None
        or getattr(obj, "__tablename__", None) is not None
    )
    has_mapper = hasattr(obj, "__mapper__")
    has_registry = hasattr(obj, "registry")  # used in SQLAlchemy v2
    if has_table and (has_mapper or has_registry):
        return True

    return False


def autodiscover_models(module_paths: List[str] | None):
    """
    Automatically discover and register all SQLAlchemy / SQLModel models
    from a list of Python module paths.

    Example:
        autodiscover_models(["myproject.models", "shop.models"])

    Steps:
      1. Import each module in the given list.
      2. Recursively walk through all its submodules (e.g., models.user, models.article).
      3. Inspect each module for classes.
      4. Check if each class is a valid SQLAlchemy/SQLModel model.
      5. Register it using `register_model()`.

    This allows automatic model discovery like Django's admin autodiscover.
    """
    for module_path in module_paths:
        try:
            # Try to import the top-level module (e.g., "shop.models")
            package = importlib.import_module(module_path)
        except ModuleNotFoundError:
            print(f"[auto-discover] package '{module_path}' not found, skipping.")
            continue

        # Collect all modules: base + submodules
        modules = [package]
        if hasattr(package, "__path__"):  # means it's a package, not a single file
            for _, modname, _ in pkgutil.walk_packages(
                package.__path__, prefix=package.__name__ + "."
            ):
                try:
                    submod = importlib.import_module(modname)
                    modules.append(submod)
                except Exception as e:
                    print(f"[auto-discover] failed to import {modname}: {e}")

        # Inspect all classes inside these modules
        for mod in modules:
            for name, obj in inspect.getmembers(mod, inspect.isclass):
                try:
                    if is_sqlalchemy_model(obj):
                        # If it's a valid model, register it for admin CRUD
                        register_model(obj)
                        print(
                            f"[auto-discover] ✅ registered model: {obj.__module__}.{obj.__name__}"
                        )
                except Exception as e:
                    print(f"[auto-discover] ⚠️ error registering {name}: {e}")
