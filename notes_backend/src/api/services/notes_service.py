from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from src.api.models import Note, Tag, User


def _normalize_tag(name: str) -> str:
    return name.strip().lower()


def _get_or_create_tags(db: Session, *, user_id: int, tag_names: list[str]) -> list[Tag]:
    normalized = []
    for n in tag_names:
        nn = _normalize_tag(n)
        if nn and nn not in normalized:
            normalized.append(nn)

    if not normalized:
        return []

    existing = db.execute(
        select(Tag).where(Tag.user_id == user_id, Tag.name.in_(normalized))
    ).scalars().all()
    existing_by_name = {t.name: t for t in existing}

    tags: list[Tag] = []
    for n in normalized:
        t = existing_by_name.get(n)
        if t is None:
            t = Tag(user_id=user_id, name=n)
            db.add(t)
        tags.append(t)
    return tags


def list_notes(
    db: Session,
    *,
    user: User,
    q: str | None,
    tag: str | None,
    pinned: bool | None,
    favorite: bool | None,
    limit: int,
    offset: int,
) -> tuple[list[Note], int]:
    stmt = select(Note).where(Note.user_id == user.id).options(joinedload(Note.tags))

    if q:
        like = f"%{q.strip().lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Note.title).like(like),
                func.lower(Note.content_md).like(like),
            )
        )

    if tag:
        t = _normalize_tag(tag)
        if t:
            stmt = stmt.join(Note.tags).where(Tag.name == t)

    if pinned is not None:
        stmt = stmt.where(Note.pinned == pinned)
    if favorite is not None:
        stmt = stmt.where(Note.favorite == favorite)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = int(db.execute(count_stmt).scalar_one())

    stmt = stmt.order_by(Note.pinned.desc(), Note.updated_at.desc()).limit(limit).offset(offset)
    items = db.execute(stmt).scalars().unique().all()
    return items, total


def get_note(db: Session, *, user: User, note_id: int) -> Note | None:
    return db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == user.id).options(joinedload(Note.tags))
    ).scalar_one_or_none()


def create_note(
    db: Session,
    *,
    user: User,
    title: str,
    content_md: str,
    pinned: bool,
    favorite: bool,
    tags: list[str],
) -> Note:
    note = Note(user_id=user.id, title=title, content_md=content_md, pinned=pinned, favorite=favorite)
    note.tags = _get_or_create_tags(db, user_id=user.id, tag_names=tags)
    db.add(note)
    db.flush()
    db.refresh(note)
    return note


def update_note(
    db: Session,
    *,
    note: Note,
    title: str | None,
    content_md: str | None,
    pinned: bool | None,
    favorite: bool | None,
    tags: list[str] | None,
) -> Note:
    if title is not None:
        note.title = title
    if content_md is not None:
        note.content_md = content_md
    if pinned is not None:
        note.pinned = pinned
    if favorite is not None:
        note.favorite = favorite
    if tags is not None:
        note.tags = _get_or_create_tags(db, user_id=note.user_id, tag_names=tags)

    db.add(note)
    db.flush()
    db.refresh(note)
    return note
