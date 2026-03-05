from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token (Bearer)")
    token_type: str = Field("bearer", description="Token type")


class UserMeResponse(BaseModel):
    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email")


class AuthRegisterRequest(BaseModel):
    email: str = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="User password (min 8 chars)")


class AuthLoginRequest(BaseModel):
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")


class TagResponse(BaseModel):
    id: int = Field(..., description="Tag ID")
    name: str = Field(..., description="Tag name")


class NoteResponse(BaseModel):
    id: int = Field(..., description="Note ID")
    title: str = Field(..., description="Note title")
    content_md: str = Field(..., description="Markdown content")
    pinned: bool = Field(..., description="Pinned state")
    favorite: bool = Field(..., description="Favorite state")
    tags: list[TagResponse] = Field(default_factory=list, description="Tags attached to this note")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC)")


class NoteCreateRequest(BaseModel):
    title: str = Field("", max_length=200, description="Note title")
    content_md: str = Field("", description="Markdown content")
    pinned: bool = Field(False, description="Pinned state")
    favorite: bool = Field(False, description="Favorite state")
    tags: list[str] = Field(default_factory=list, description="Tag names to attach (created if missing)")


class NoteUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=200, description="Note title")
    content_md: Optional[str] = Field(None, description="Markdown content")
    pinned: Optional[bool] = Field(None, description="Pinned state")
    favorite: Optional[bool] = Field(None, description="Favorite state")
    tags: Optional[list[str]] = Field(None, description="Replace tags with these names (creates missing)")


class NoteListResponse(BaseModel):
    items: list[NoteResponse] = Field(default_factory=list, description="Notes")
    total: int = Field(..., description="Total matching notes (before paging)")
