# AI Image Organizer (Prototype)

Minimal FastAPI backend that ingests images, extracts CLIP embeddings, clusters them with MiniBatchKMeans, and exposes REST endpoints for future UI integrations.

## Features

- Upload images and persist metadata + CLIP embeddings in SQLite via SQLModel.
- Compute feature vectors using a pretrained `openai/clip-vit-base-patch32` model (CPU by default).
- Generate simple image clusters on demand with scikit-learn `MiniBatchKMeans`.
- Ready for integration with a frontend UI or CLI client.

## Getting Started

### Using uv (Recommended)

```bash
# Create virtual environment
uv venv

# Activate the environment
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows

# Install dependencies
uv pip install -r requirements.txt

# Run the server using uv
uv run uvicorn backend.app.main:app --reload

# Or use the convenience script
./run.sh
```

### Alternative: Using pip

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. Interactive docs at `/docs`.

## Testing the Application

### Option 1: Web Test Interface

1. Start the server: `./run.sh`
2. Open `test.html` in your browser (double-click the file or open it via `file://` URL)
3. The test interface allows you to:
   - Check API health
   - Upload images (drag & drop or click to select)
   - View all uploaded images
   - Generate and view image clusters

### Option 2: FastAPI Interactive Docs

1. Start the server: `./run.sh`
2. Open `http://127.0.0.1:8000/docs` in your browser
3. Use the interactive Swagger UI to test endpoints:
   - Try `POST /images` to upload an image
   - Try `GET /images` to list all images
   - Try `GET /clusters` to see image clusters
   - Try `GET /health` for health check

### Option 3: Command Line (curl)

```bash
# Health check
curl http://127.0.0.1:8000/health

# Upload an image
curl -X POST "http://127.0.0.1:8000/images" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/image.jpg"

# List all images
curl http://127.0.0.1:8000/images

# Get clusters
curl http://127.0.0.1:8000/clusters
```

### Environment Variables

Create a `.env` file to override defaults:

```
APP_NAME=AI Image Organizer
DATABASE_URL=sqlite+aiosqlite:///./image_organizer.db
STORAGE_ROOT=storage
CLIP_MODEL_NAME=openai/clip-vit-base-patch32
CLIP_DEVICE=cpu
KMEANS_CLUSTERS=8
KMEANS_BATCH_SIZE=64
```

## API Overview

- `POST /images`: multipart upload (`file`) -> stores image, returns metadata.
- `GET /images`: list stored images.
- `GET /clusters`: recompute clusters from stored embeddings.
- `GET /health`: health check.

## Project Structure

```
backend/
  app/
    main.py          # FastAPI app & wiring
    config.py        # Settings (env driven)
    database.py      # Async SQLModel setup
    models.py        # Image table definition
    schemas.py       # Pydantic response models
    services/        # Business logic (ingestion, clustering)
    routers/         # API routes for images & clusters
ml/
  clip_embedder.py  # CLIP model wrapper
  clusterer.py      # MiniBatchKMeans helper
storage/            # Local image storage (gitignored)
docs/architecture.md
requirements.txt
```

## Next Steps

- Add background workers for embedding extraction and clustering updates.
- Swap SQLite for Postgres + pgvector or a dedicated vector database.
- Expose semantic search endpoints using CLIP text encoder.
- Build frontend to explore clusters and tag images.
