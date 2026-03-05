from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.core.config import get_settings
from src.api.routes.auth import router as auth_router
from src.api.routes.notes import router as notes_router
from src.api.routes.tags import router as tags_router

settings = get_settings()

openapi_tags = [
    {"name": "health", "description": "Health and status endpoints."},
    {"name": "auth", "description": "Authentication endpoints (register/login/me)."},
    {"name": "notes", "description": "Notes CRUD, search, filters."},
    {"name": "tags", "description": "Tag listing for filtering/sidebar."},
]

app = FastAPI(
    title="NoteMaster API",
    description="Backend API for NoteMaster: auth + notes (Markdown) + tags + search + pinned/favorite.",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(notes_router)
app.include_router(tags_router)


@app.get(
    "/",
    tags=["health"],
    summary="Health check",
    description="Simple health endpoint.",
    operation_id="health_check",
)
# PUBLIC_INTERFACE
def health_check():
    """Health check endpoint.

    Returns:
        JSON object indicating service is running.
    """
    return {"message": "Healthy"}
