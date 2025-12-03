from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel
from sqlalchemy import Column
from sqlalchemy.types import LargeBinary


class Image(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    original_filename: str
    content_type: str
    size_bytes: int
    storage_path: str
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    embedding: Optional[bytes] = Field(default=None, sa_column=Column(LargeBinary))
    object_category: Optional[str] = None  # e.g., "cat", "dog", "car"
    background_category: Optional[str] = None  # e.g., "indoor", "outdoor"
