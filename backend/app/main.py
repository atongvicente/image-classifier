from __future__ import annotations

from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import init_database
from .routers import clusters, images
from .services.image_service import ImageService
from ml.clip_embedder import ClipEmbedder
from ml.clusterer import Clusterer

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    embedder = ClipEmbedder(
        settings.clip_model_name,
        settings.clip_device,
        use_augmentation=settings.clip_use_augmentation,
        num_augmentations=settings.clip_num_augmentations,
    )
    clusterer = Clusterer(
        method=settings.clustering_method,
        n_clusters=settings.kmeans_clusters,
        batch_size=settings.kmeans_batch_size,
        min_cluster_size=settings.hdbscan_min_cluster_size,
        min_samples=settings.hdbscan_min_samples,
    )
    app.state.settings = settings
    app.state.image_service = ImageService(settings, embedder, clusterer)
    await init_database()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(images.router)
app.include_router(clusters.router)

# Serve static files from storage directory (only if not using Cloudinary)
if not settings.use_cloudinary:
    app.mount("/storage", StaticFiles(directory=str(settings.storage_root)), name="storage")


@app.get("/")
async def root():
    return {
        "message": "AI Image Organizer API",
        "docs": "/docs",
        "test_ui": "/test.html",
        "health": "/health",
        "endpoints": {
            "upload_image": "POST /images",
            "list_images": "GET /images",
            "get_clusters": "GET /clusters"
        }
    }


@app.get("/test.html")
async def test_page():
    """Serve the test HTML interface"""
    test_file = Path(__file__).parent.parent.parent / "test.html"
    return FileResponse(test_file)


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
