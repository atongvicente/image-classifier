from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from ..dependencies import get_db_session, get_image_service
from ..schemas import CategoryGroup, ClusterInfo
from ..services.image_service import ImageService

router = APIRouter(prefix="/clusters", tags=["clusters"])


@router.get("", response_model=List[ClusterInfo])
async def list_clusters(
    service: ImageService = Depends(get_image_service),
    session: AsyncSession = Depends(get_db_session),
) -> List[ClusterInfo]:
    """Get flat list of clusters (for backward compatibility)"""
    return await service.get_clusters(session)


@router.get("/grouped", response_model=List[CategoryGroup])
async def list_clusters_grouped(
    service: ImageService = Depends(get_image_service),
    session: AsyncSession = Depends(get_db_session),
) -> List[CategoryGroup]:
    """Get clusters grouped by object category with background subgroups"""
    clusters = await service.get_clusters(session)
    
    # Group clusters by object category
    groups: dict[str, list[ClusterInfo]] = {}
    for cluster in clusters:
        obj_cat = cluster.object_category or "unknown"
        if obj_cat not in groups:
            groups[obj_cat] = []
        groups[obj_cat].append(cluster)
    
    # Create CategoryGroup objects
    category_groups = []
    for obj_cat, cluster_list in groups.items():
        total_images = sum(len(c.image_ids) for c in cluster_list)
        category_groups.append(
            CategoryGroup(
                object_category=obj_cat,
                total_images=total_images,
                subgroups=cluster_list,
            )
        )
    
    # Sort by object category name
    category_groups.sort(key=lambda x: x.object_category)
    
    return category_groups
