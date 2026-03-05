from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.api.core.db import get_db
from src.api.deps import get_current_user
from src.api.models import Tag, User
from src.api.schemas import TagResponse

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get(
    "",
    response_model=list[TagResponse],
    summary="List tags",
    description="List all tags for the current user (for filtering/sidebar).",
    operation_id="tags_list",
)
def tags_list(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TagResponse]:
    """List tags for the current user."""
    tags = db.execute(select(Tag).where(Tag.user_id == user.id).order_by(func.lower(Tag.name))).scalars().all()
    return [TagResponse(id=t.id, name=t.name) for t in tags]
