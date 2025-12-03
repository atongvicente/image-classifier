from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Image Organizer"
    database_url: str = "sqlite+aiosqlite:///./image_organizer.db"
    storage_root: Path = Path("storage")
    
    # Cloudinary settings
    use_cloudinary: bool = False
    cloudinary_cloud_name: Optional[str] = None
    cloudinary_api_key: Optional[str] = None
    cloudinary_api_secret: Optional[str] = None
    
    # CLIP settings
    clip_model_name: str = "openai/clip-vit-base-patch32"
    clip_device: str = "cpu"
    clip_use_augmentation: bool = True
    clip_num_augmentations: int = 3
    
    # Clustering settings
    clustering_method: str = "hdbscan"  # "hdbscan" or "kmeans"
    kmeans_clusters: int = 8
    kmeans_batch_size: int = 64
    hdbscan_min_cluster_size: int = 2
    hdbscan_min_samples: Optional[int] = None

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()
