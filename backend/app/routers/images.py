from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, File, UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession

from ..dependencies import get_db_session, get_image_service
from ..schemas import ImageRead
from ..services.image_service import ImageService

router = APIRouter(prefix="/images", tags=["images"])


@router.post("", response_model=ImageRead)
async def upload_image(
    file: UploadFile = File(...),
    service: ImageService = Depends(get_image_service),
    session: AsyncSession = Depends(get_db_session),
) -> ImageRead:
    image = await service.ingest_image(file, session)
    image_data = ImageRead.model_validate(image)
    # Add image URL from storage service
    image_data.image_url = service.storage.get_image_url(image.storage_path)
    return image_data


@router.get("", response_model=List[ImageRead])
async def list_images(
    service: ImageService = Depends(get_image_service),
    session: AsyncSession = Depends(get_db_session),
) -> List[ImageRead]:
    images = await service.list_images(session)
    result = []
    for record in images:
        image_data = ImageRead.model_validate(record)
        # Add image URL from storage service
        image_data.image_url = service.storage.get_image_url(record.storage_path)
        result.append(image_data)
    return result
