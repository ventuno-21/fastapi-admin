import typer
import asyncio
from .db import AsyncSessionLocal, init_db
from . import crud

# Create a Typer app (the CLI application)
app = typer.Typer()

"""
    Typer turns your Python functions into professional CLI commands with minimal 
    code — here, it gives your FastAPI app an easy way to manage users from the terminal,
    similar to Django’s createsuperuser.

    This lets you run your script from the terminal like this:

    python -m my_admin_pkg.cli createsuperuser --email admin@example.com

    Then Typer:

    Prompts you for a password (hidden input),
    Runs your asynchronous database logic via asyncio.run(),
    Creates the admin user,
   And prints a success message.

"""


@app.command()
def createsuperuser(
    username: str = typer.Option(...),
    email: str = typer.Option(...),
):
    """
    Create a superuser (blocking wrapper around async)
    This command allows the admin to create a superuser via the CLI.
    """
    password = getpass("Password: ")
    password2 = getpass("Password (again): ")
    if password != password2:
        typer.echo("Passwords do not match.")
        raise typer.Exit(code=1)

    # Define an asynchronous inner function
    async def _create():
        # Initialize the database (create tables if needed)
        await init_db()

        # Open an async database session
        async with AsyncSessionLocal() as db:
            # Check if a user with this email already exists
            existing = await crud.get_user_by_username_or_email(db, username)
            if existing:
                typer.echo("User already exists (by username or email).")
                raise typer.Exit(code=1)

            # If not, create a new superuser
            user = await crud.create_user(
                db, email=email, password=password, is_superuser=True
            )

            # Print success message
            typer.echo(f"Created superuser {user.email} (id={user.id})")

    # Run the async code in a synchronous CLI context
    asyncio.run(_create())


# Run the Typer CLI app if executed directly
if __name__ == "__main__":
    app()
