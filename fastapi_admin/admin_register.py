from typing import Type, Any

# Dictionary to store all registered models (works for both SQLModel and SQLAlchemy)
registered_models: dict[str, Type[Any]] = {}


def register_model(model: Type[Any]):
    """
    Simple registry to keep track of discovered/registered models for the admin.

    Register a model class for the admin panel.
    Supports both SQLModel and SQLAlchemy (v1 & v2) models.

    Args:
        model: The model class to register.

    Behavior:
        - Extracts the model's table name (from __tablename__ if available).
        - Falls back to the lowercase class name if no __tablename__ is defined.
        - Saves the model into the global `registered_models` dictionary.
    """
    # Determine the model's name (table name or class name)
    name = getattr(model, "__tablename__", None) or model.__name__.lower()
    registered_models[name] = model


def get_registered_models():
    """
    Return the dictionary of all registered models.
    Used by the admin system to list, query, or generate CRUD views dynamically.
    """
    return registered_models
