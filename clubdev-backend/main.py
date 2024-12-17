import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.routing import APIRoute
from rich.console import Console
from rich.table import Table
from sqlalchemy import inspect

from app.api.routers.admin_action_api import admin_action_router
from app.api.routers.auth_api import auth_router
from app.api.routers.content_api import content_router
from app.api.routers.gamification_api import gamification_router
from app.api.routers.github_repo_api import github_repo_router
from app.api.routers.help_api import help_router
from app.api.routers.interaction_api import interaction_router
from app.api.routers.social_api import social_router
from app.api.routers.subscription_api import subscription_router
from app.api.routers.user_api import user_router
from app.db.database import create_db_and_tables, engine
from app.core.middlewares import init_middlewares

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger('passlib').setLevel(logging.ERROR)

console = Console()

@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    try:
        logger.info("Starting application lifespan...")
        logger.info("Creating database tables...")
        create_db_and_tables()
        logger.info("Database tables created successfully.")
        yield
    except Exception as lifespan_error:
        logger.error(f"Error during application lifespan: {lifespan_error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        logger.info("Ending application lifespan...")

app = FastAPI(
    title="ClubDev",
    description="ClubDev Backend",
    version="0.1.0",
    docs_url="/",
    lifespan=lifespan
)
init_middlewares(app)
logger.info("Middlewares initialized successfully.")

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(content_router, prefix="/api")
app.include_router(admin_action_router, prefix="/api")
app.include_router(interaction_router, prefix="/api")
app.include_router(help_router, prefix="/api")
app.include_router(gamification_router, prefix="/api")
app.include_router(github_repo_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(subscription_router, prefix="/api")
app.include_router(social_router, prefix="/api")

# Log all routes
route_table = Table(title="API Routes")
route_table.add_column("Path", justify="left", style="cyan", no_wrap=True)
route_table.add_column("Method", justify="left", style="magenta")
route_table.add_column("Name", justify="left", style="green")

for route in app.routes:
    if isinstance(route, APIRoute):
        route_table.add_row(route.path, ", ".join(route.methods), route.name)

console.print(route_table)

# Log all tables in the database
inspector = inspect(engine)
table_names = inspector.get_table_names()

db_table = Table(title="Database Tables")
db_table.add_column("Table Name", justify="left", style="cyan", no_wrap=True)

for table_name in table_names:
    db_table.add_row(table_name)

console.print(db_table)

if __name__ == "__main__":
    logger.info("Starting Uvicorn server...")
    uvicorn.run(app, host="localhost", port=8000)
    logger.info("Uvicorn server stopped.")