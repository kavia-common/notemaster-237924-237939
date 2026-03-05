from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.core.db import get_db
from src.api.deps import get_current_user
from src.api.models import Note, User
from src.api.schemas import NoteCreateRequest, NoteListResponse, NoteResponse, NoteUpdateRequest, TagResponse
from src.api.services.notes_service import create_note, get_note, list_notes, update_note

router = APIRouter(prefix="/notes", tags=["notes"])


def _to_note_response(note: Note) -> NoteResponse:
    return NoteResponse(
        id=note.id,
        title=note.title,
        content_md=note.content_md,
        pinned=note.pinned,
        favorite=note.favorite,
        tags=[TagResponse(id=t.id, name=t.name) for t in sorted(note.tags, key=lambda x: x.name)],
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


@router.get(
    "",
    response_model=NoteListResponse,
    summary="List notes",
    description="List notes with optional search query, tag filter, and pinned/favorite filters.",
    operation_id="notes_list",
)
def notes_list(
    q: str | None = Query(None, description="Full-text search against title/content (ILIKE emulation)"),
    tag: str | None = Query(None, description="Filter by tag name"),
    pinned: bool | None = Query(None, description="Filter by pinned state"),
    favorite: bool | None = Query(None, description="Filter by favorite state"),
    limit: int = Query(50, ge=1, le=200, description="Page size"),
    offset: int = Query(0, ge=0, description="Offset for paging"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NoteListResponse:
    """List notes for the current user."""
    items, total = list_notes(db, user=user, q=q, tag=tag, pinned=pinned, favorite=favorite, limit=limit, offset=offset)
    return NoteListResponse(items=[_to_note_response(n) for n in items], total=total)


@router.post(
    "",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create note",
    description="Create a new note (Markdown) with optional tags.",
    operation_id="notes_create",
)
def notes_create(
    payload: NoteCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NoteResponse:
    """Create a note for the current user."""
    note = create_note(
        db,
        user=user,
        title=payload.title,
        content_md=payload.content_md,
        pinned=payload.pinned,
        favorite=payload.favorite,
        tags=payload.tags,
    )
    db.commit()
    db.refresh(note)
    return _to_note_response(note)


@router.get(
    "/{note_id}",
    response_model=NoteResponse,
    summary="Get note",
    description="Fetch a single note by id.",
    operation_id="notes_get",
)
def notes_get(
    note_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NoteResponse:
    """Get a note."""
    note = get_note(db, user=user, note_id=note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return _to_note_response(note)


@router.put(
    "/{note_id}",
    response_model=NoteResponse,
    summary="Update note",
    description="Update fields of a note; tags (if provided) replace existing tags.",
    operation_id="notes_update",
)
def notes_update(
    note_id: int,
    payload: NoteUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NoteResponse:
    """Update a note."""
    note = get_note(db, user=user, note_id=note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    note = update_note(
        db,
        note=note,
        title=payload.title,
        content_md=payload.content_md,
        pinned=payload.pinned,
        favorite=payload.favorite,
        tags=payload.tags,
    )
    db.commit()
    db.refresh(note)
    return _to_note_response(note)


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete note",
    description="Delete a note by id.",
    operation_id="notes_delete",
)
def notes_delete(
    note_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Delete a note."""
    note = get_note(db, user=user, note_id=note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return None
