from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
from uuid import uuid4

try:
    import cloudinary
    import cloudinary.uploader
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False


class StorageService(ABC):
    """Abstract base class for storage services"""
    
    @abstractmethod
    def upload_image(self, data: bytes, original_name: str) -> str:
        """Upload image and return storage path/URL"""
        pass
    
    @abstractmethod
    def get_image_url(self, storage_path: str) -> str:
        """Get public URL for an image"""
        pass


class LocalStorageService(StorageService):
    """Local filesystem storage"""
    
    def __init__(self, storage_root: Path) -> None:
        self.storage_root = storage_root
        self.storage_root.mkdir(parents=True, exist_ok=True)
    
    def upload_image(self, data: bytes, original_name: str) -> str:
        sanitized_name = original_name.replace("/", "_")
        filename = f"{uuid4().hex}_{sanitized_name}"
        path = self.storage_root / filename
        
        with path.open("wb") as f:
            f.write(data)
        
        return str(path)
    
    def get_image_url(self, storage_path: str) -> str:
        # Extract filename from path
        filename = Path(storage_path).name
        return f"/storage/{filename}"


class CloudinaryStorageService(StorageService):
    """Cloudinary cloud storage"""
    
    def __init__(
        self,
        cloud_name: str,
        api_key: str,
        api_secret: str,
        folder: str = "ai-image-organizer",
    ) -> None:
        if not CLOUDINARY_AVAILABLE:
            raise ImportError("cloudinary package is not installed. Install it with: pip install cloudinary")
        
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
        )
        self.folder = folder
    
    def upload_image(self, data: bytes, original_name: str) -> str:
        """Upload to Cloudinary and return public_id"""
        sanitized_name = original_name.replace("/", "_")
        public_id = f"{self.folder}/{uuid4().hex}_{sanitized_name}"
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            data,
            public_id=public_id,
            resource_type="image",
            folder=self.folder,
        )
        
        # Store public_id in database (not full URL, as it can be generated)
        return result["public_id"]
    
    def get_image_url(self, storage_path: str) -> str:
        """Generate Cloudinary URL from public_id"""
        # storage_path is the public_id
        return cloudinary.CloudinaryImage(storage_path).build_url(
            secure=True,
            transformation=[
                {"width": 800, "height": 800, "crop": "limit", "quality": "auto"},
            ],
        )

