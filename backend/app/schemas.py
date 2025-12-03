from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ImageCreate(BaseModel):
    pass  # Placeholder for future body params (e.g., tags)


class ImageRead(BaseModel):
    id: int
    original_filename: str
    content_type: str
    size_bytes: int
    storage_path: str
    image_url: Optional[str] = None  # Public URL for the image
    width: Optional[int]
    height: Optional[int]
    created_at: datetime
    object_category: Optional[str] = None
    background_category: Optional[str] = None

    class Config:
        from_attributes = True


class ClusterInfo(BaseModel):
    cluster_id: int
    category_name: str  # e.g., "cat - indoor", "dog - outdoor"
    object_category: Optional[str] = None
    background_category: Optional[str] = None
    centroid: list[float]
    image_ids: list[int]


class CategoryGroup(BaseModel):
    """Groups clusters by main object category"""
    object_category: str
    total_images: int
    subgroups: list[ClusterInfo]  # Clusters grouped by background
