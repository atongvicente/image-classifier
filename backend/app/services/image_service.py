from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import List
from uuid import uuid4

import numpy as np
from fastapi import UploadFile
from PIL import Image as PILImage
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..config import Settings
from ..models import Image
from ..schemas import ClusterInfo
from ml.clip_embedder import ClipEmbedder
from ml.clusterer import Clusterer
from .storage_service import (
    CloudinaryStorageService,
    LocalStorageService,
    StorageService,
)


class ImageService:
    def __init__(self, settings: Settings, embedder: ClipEmbedder, clusterer: Clusterer) -> None:
        self.settings = settings
        self.embedder = embedder
        self.clusterer = clusterer
        self.storage: StorageService = self._init_storage()

    def _init_storage(self) -> StorageService:
        """Initialize storage service based on configuration"""
        if self.settings.use_cloudinary and all([
            self.settings.cloudinary_cloud_name,
            self.settings.cloudinary_api_key,
            self.settings.cloudinary_api_secret,
        ]):
            return CloudinaryStorageService(
                cloud_name=self.settings.cloudinary_cloud_name,
                api_key=self.settings.cloudinary_api_key,
                api_secret=self.settings.cloudinary_api_secret,
            )
        else:
            return LocalStorageService(self.settings.storage_root)

    async def ingest_image(self, file: UploadFile, session: AsyncSession) -> Image:
        data = await file.read()
        original_name = file.filename or f"upload-{uuid4().hex}"
        storage_path = self.storage.upload_image(data, original_name)
        width, height = self._get_dimensions(data)
        embedding = self.embedder.encode_image(data)
        
        # Classify object and background
        object_category = self.embedder.classify_object(data)
        background_category = self.embedder.classify_background(data)

        image = Image(
            original_filename=original_name,
            content_type=file.content_type or "application/octet-stream",
            size_bytes=len(data),
            storage_path=storage_path,
            width=width,
            height=height,
            embedding=embedding.tobytes(),
            object_category=object_category,
            background_category=background_category,
        )
        session.add(image)
        await session.flush()
        return image

    def _get_dimensions(self, data: bytes) -> tuple[int, int]:
        with PILImage.open(BytesIO(data)) as img:
            return img.size

    async def list_images(self, session: AsyncSession) -> List[Image]:
        result = await session.exec(select(Image))
        return result.all()

    async def get_clusters(self, session: AsyncSession) -> List[ClusterInfo]:
        result = await session.exec(select(Image))
        records = result.all()
        
        if not records:
            return []

        # Group by object category first, then by background
        # This creates a two-level grouping: object -> background -> images
        category_groups: dict[tuple[str, str], list[tuple[int, np.ndarray]]] = {}
        
        for record in records:
            if record.embedding and record.object_category:
                obj_cat = record.object_category
                bg_cat = record.background_category or "unknown"
                key = (obj_cat, bg_cat)
                
                if key not in category_groups:
                    category_groups[key] = []
                
                embedding = np.frombuffer(record.embedding, dtype=np.float32)
                category_groups[key].append((record.id, embedding))

        clusters: list[ClusterInfo] = []
        cluster_id = 0

        # For each object+background combination, use clustering if multiple images
        for (object_category, bg_cat), image_records in category_groups.items():
            image_ids = [rid for rid, _ in image_records]
            embeddings = [emb for _, emb in image_records]
            
            if len(embeddings) == 1:
                # Single image - no clustering needed
                category_name = f"{object_category} - {bg_cat}"
                clusters.append(
                    ClusterInfo(
                        cluster_id=cluster_id,
                        category_name=category_name,
                        object_category=object_category,
                        background_category=bg_cat,
                        centroid=embeddings[0].tolist(),
                        image_ids=image_ids,
                    )
                )
                cluster_id += 1
            else:
                # Multiple images - apply clustering to find natural subgroups
                matrix = np.vstack(embeddings)
                labels, centroids = self.clusterer.cluster_embeddings(matrix)
                
                # Handle HDBSCAN noise points (label -1) - put them in a separate cluster
                unique_labels = np.unique(labels)
                unique_labels = unique_labels[unique_labels != -1]  # Remove noise label
                
                if len(unique_labels) == 0:
                    # All points are noise - treat as one cluster
                    category_name = f"{object_category} - {bg_cat}"
                    centroid = matrix.mean(axis=0).tolist()
                    clusters.append(
                        ClusterInfo(
                            cluster_id=cluster_id,
                            category_name=category_name,
                            object_category=object_category,
                            background_category=bg_cat,
                            centroid=centroid,
                            image_ids=image_ids,
                        )
                    )
                    cluster_id += 1
                else:
                    # Create a cluster for each detected sub-cluster
                    for label_idx, label in enumerate(unique_labels):
                        clustered_ids = [image_ids[i] for i, lbl in enumerate(labels) if lbl == label]
                        centroid = centroids[label_idx].tolist()
                        
                        # Add sub-cluster suffix if multiple clusters exist
                        if len(unique_labels) > 1:
                            category_name = f"{object_category} - {bg_cat} (group {label_idx + 1})"
                        else:
                            category_name = f"{object_category} - {bg_cat}"
                        
                        clusters.append(
                            ClusterInfo(
                                cluster_id=cluster_id,
                                category_name=category_name,
                                object_category=object_category,
                                background_category=bg_cat,
                                centroid=centroid,
                                image_ids=clustered_ids,
                            )
                        )
                        cluster_id += 1
                    
                    # Handle noise points separately if any
                    noise_ids = [image_ids[i] for i, lbl in enumerate(labels) if lbl == -1]
                    if len(noise_ids) > 0:
                        noise_embeddings = [embeddings[i] for i, lbl in enumerate(labels) if lbl == -1]
                        noise_centroid = np.vstack(noise_embeddings).mean(axis=0).tolist()
                        clusters.append(
                            ClusterInfo(
                                cluster_id=cluster_id,
                                category_name=f"{object_category} - {bg_cat} (outliers)",
                                object_category=object_category,
                                background_category=bg_cat,
                                centroid=noise_centroid,
                                image_ids=noise_ids,
                            )
                        )
                        cluster_id += 1

        return clusters
