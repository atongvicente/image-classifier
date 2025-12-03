# AI Image Organizer — Architecture & Deployment

> 📊 **Visual Diagram**: See [architecture-diagram.md](./architecture-diagram.md) for detailed visual representations

## System Overview

The AI Image Organizer is a production-ready application that uses CLIP-based feature extraction, test-time augmentation, and intelligent clustering to organize images by object category and background. It supports both local and cloud storage (Cloudinary) and can be deployed on AWS free tier.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Web UI (test.html)                                      │   │
│  │  - Image Upload (drag & drop)                            │   │
│  │  - Hierarchical Cluster Visualization                   │   │
│  │  - Category Display (Object + Background)               │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────────┐
│                      API Backend (FastAPI)                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  REST Endpoints                                           │   │
│  │  - POST /images (upload)                                 │   │
│  │  - GET /images (list)                                    │   │
│  │  - GET /clusters (grouped by category)                  │   │
│  │  - GET /clusters/grouped (hierarchical)                  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      ML Service Layer                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  CLIP Embedder                                            │   │
│  │  ├── Model: openai/clip-vit-base-patch32                 │   │
│  │  ├── Image → Embedding (512-dim vector)                  │   │
│  │  └── Text-Image Similarity (classification)              │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Test-Time Augmentation (Albumentations)                 │   │
│  │  ├── Horizontal Flip                                    │   │
│  │  ├── Brightness/Contrast                                │   │
│  │  ├── Gamma Correction                                   │   │
│  │  ├── CLAHE (Adaptive Histogram)                         │   │
│  │  └── Gaussian Noise                                     │   │
│  │  → Multiple views → Averaged embeddings                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Classification                                          │   │
│  │  ├── Object Category (cat, dog, car, etc.)              │   │
│  │  └── Background Category (indoor, outdoor, etc.)        │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Clustering Engine                                       │   │
│  │  ├── HDBSCAN (density-based, auto-clusters)             │   │
│  │  └── MiniBatchKMeans (alternative)                      │   │
│  │  → Hierarchical: Object → Background → Sub-clusters      │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Storage Layer                               │
│  ┌──────────────────────┐         ┌──────────────────────┐    │
│  │  Cloudinary Storage   │         │  Local Filesystem     │    │
│  │  (Cloud - Production) │         │  (Development)        │    │
│  │  ├── Auto CDN        │         │  ├── /storage/        │    │
│  │  ├── Image Transform │         │  └── Static serving   │    │
│  │  └── 25GB Free Tier  │         │                       │    │
│  └──────────────────────┘         └──────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Database Layer                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  SQLite (Development) / PostgreSQL (Production)          │   │
│  │  ├── Image Metadata (filename, size, dimensions)         │   │
│  │  ├── CLIP Embeddings (binary, 512-dim)                  │   │
│  │  ├── Object Category                                     │   │
│  │  └── Background Category                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    AWS Deployment Options                        │
│  ┌──────────────────────┐         ┌──────────────────────┐    │
│  │  EC2 (t2.micro)      │         │  App Runner          │    │
│  │  ├── CloudFormation  │         │  (Serverless)        │    │
│  │  ├── VPC + Security  │         │  ├── Auto-scaling    │    │
│  │  ├── Systemd Service │         │  ├── GitHub Deploy  │    │
│  │  └── Free Tier:      │         │  └── Free Tier:      │    │
│  │      750 hrs/month    │         │      750 hrs/month   │    │
│  └──────────────────────┘         └──────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### Frontend Layer
- **Web UI** (`test.html`): Interactive interface for image upload, visualization, and cluster exploration
- **Features**: Drag & drop upload, hierarchical cluster display, category filtering
- **API Communication**: RESTful HTTP requests to FastAPI backend

### API Backend (FastAPI)
- **REST Endpoints**:
  - `POST /images` - Upload images with automatic classification
  - `GET /images` - List all images with metadata and URLs
  - `GET /clusters` - Get flat cluster list
  - `GET /clusters/grouped` - Get hierarchical clusters (Object → Background → Images)
  - `GET /health` - Health check
- **CORS**: Enabled for web frontend access
- **Static File Serving**: Local storage endpoint (when not using Cloudinary)

### ML Service Layer

#### CLIP Embedder
- **Model**: `openai/clip-vit-base-patch32` via Hugging Face Transformers
- **Features**:
  - Image → 512-dimensional embedding vector
  - Text-image similarity for classification
  - Object category detection (cat, dog, car, person, etc.)
  - Background category detection (indoor, outdoor, urban, etc.)

#### Test-Time Augmentation (TTA)
- **Library**: Albumentations
- **Augmentations**:
  - Horizontal flip (50% probability)
  - Brightness/Contrast adjustment (50% probability)
  - Gamma correction (30% probability)
  - CLAHE - Adaptive histogram equalization (30% probability)
  - Gaussian noise (20% probability)
- **Process**: Create 3 augmented views → Extract embeddings → Average for robustness
- **Benefit**: Improves classification accuracy by handling lighting/angle variations

#### Clustering Engine
- **Primary**: HDBSCAN (Hierarchical Density-Based Spatial Clustering)
  - Automatically determines number of clusters
  - Handles varying cluster densities
  - Identifies noise/outlier points
- **Alternative**: MiniBatchKMeans (faster, requires cluster count)
- **Hierarchical Structure**:
  1. Group by Object Category (cat, dog, car, etc.)
  2. Sub-group by Background (indoor, outdoor, etc.)
  3. Further sub-cluster within same category using embeddings

### Storage Layer

#### Cloudinary (Production)
- **Features**:
  - Automatic CDN delivery
  - Image transformations on-the-fly
  - Free tier: 25GB storage, 25GB bandwidth/month
  - Secure URLs with transformations
- **Integration**: Seamless fallback to local storage if not configured

#### Local Filesystem (Development)
- **Path**: `storage/` directory
- **Serving**: FastAPI static file mount at `/storage`
- **Use Case**: Development and testing

### Database Layer

#### SQLite (Development)
- **Location**: `image_organizer.db`
- **Schema**: Image metadata, embeddings, categories
- **ORM**: SQLModel with async support

#### PostgreSQL (Production - Optional)
- **Use Case**: Production deployments with RDS
- **Driver**: `asyncpg` for async operations
- **Benefits**: Better concurrency, scalability

### AWS Deployment Infrastructure

#### EC2 Option
- **Instance**: t2.micro (free tier: 750 hrs/month)
- **Infrastructure**: VPC, Security Groups, IAM Roles
- **Deployment**: CloudFormation template with UserData script
- **Service Management**: Systemd service for auto-restart

#### App Runner Option
- **Type**: Serverless container service
- **Deployment**: Direct from GitHub repository
- **Scaling**: Auto-scaling based on traffic
- **Free Tier**: 750 hours/month
- **Benefits**: Zero server management, automatic HTTPS

## Data Flow

### Image Upload Flow
```
1. User uploads image via Frontend
   ↓
2. FastAPI receives multipart/form-data
   ↓
3. Storage Service:
   - If Cloudinary: Upload to cloud → Get public_id
   - If Local: Save to filesystem → Get file path
   ↓
4. ML Processing Pipeline:
   a. Test-Time Augmentation:
      - Create 3 augmented versions
      - Extract CLIP embeddings for each
      - Average embeddings for robustness
   b. Classification:
      - Object category (via text-image similarity)
      - Background category (via text-image similarity)
   ↓
5. Database Storage:
   - Save metadata (filename, size, dimensions)
   - Save averaged embedding (512-dim vector)
   - Save object_category and background_category
   - Save storage_path (Cloudinary public_id or file path)
   ↓
6. Return response with image_url (Cloudinary URL or local path)
```

### Clustering Flow
```
1. Client requests GET /clusters/grouped
   ↓
2. Retrieve all images with embeddings from database
   ↓
3. Group by Object Category:
   - cat → [all cat images]
   - dog → [all dog images]
   - etc.
   ↓
4. For each object category, group by Background:
   - cat → indoor → [indoor cat images]
   - cat → outdoor → [outdoor cat images]
   ↓
5. Apply Clustering (if multiple images in same category):
   - Use HDBSCAN to find natural sub-groups
   - Handle noise/outliers separately
   ↓
6. Return hierarchical structure:
   {
     "object_category": "cat",
     "total_images": 5,
     "subgroups": [
       {
         "background_category": "indoor",
         "image_ids": [1, 2, 3]
       },
       {
         "background_category": "outdoor",
         "image_ids": [4, 5]
       }
     ]
   }
```

## Operational Considerations

### Performance
- **Model Loading**: CLIP model cached after first download (~150MB)
- **Augmentation**: Increases processing time ~3x but improves accuracy
- **Clustering**: HDBSCAN slower than KMeans but provides better quality
- **Storage**: Cloudinary provides CDN, reducing latency globally

### Scalability
- **Current**: Handles hundreds of images efficiently
- **Future Enhancements**:
  - Background workers (Celery/RQ) for async processing
  - GPU acceleration for CLIP (set `CLIP_DEVICE=cuda`)
  - Vector database (Pinecone, Weaviate) for large-scale similarity search
  - Caching cluster results instead of recomputing

### Security
- **Production Recommendations**:
  - Add API authentication (JWT tokens, API keys)
  - MIME type validation for uploads
  - Rate limiting on upload endpoints
  - Input sanitization
  - HTTPS only (via AWS ALB/CloudFront)

### Monitoring
- **Health Checks**: `/health` endpoint
- **Logging**: FastAPI automatic request logging
- **Metrics**: CloudWatch integration (AWS)
- **Error Tracking**: Consider Sentry for production

## Deployment Architecture

### Development
```
Local Machine
├── FastAPI (uvicorn)
├── SQLite Database
├── Local Storage (/storage)
└── Test UI (test.html)
```

### Production (AWS)
```
┌─────────────────────────────────────────┐
│  AWS Infrastructure                     │
│  ┌───────────────────────────────────┐ │
│  │  EC2 t2.micro or App Runner       │ │
│  │  ├── FastAPI Application          │ │
│  │  ├── Systemd Service (EC2)        │ │
│  │  └── Auto-scaling (App Runner)    │ │
│  └───────────────────────────────────┘ │
│  ┌───────────────────────────────────┐ │
│  │  Cloudinary                        │ │
│  │  ├── Image Storage                 │ │
│  │  ├── CDN Delivery                  │ │
│  │  └── Transformations               │ │
│  └───────────────────────────────────┘ │
│  ┌───────────────────────────────────┐ │
│  │  SQLite (or RDS PostgreSQL)       │ │
│  │  └── Metadata + Embeddings        │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | HTML/CSS/JavaScript | Web UI |
| **API** | FastAPI, Uvicorn | REST API server |
| **ML Model** | CLIP (Transformers) | Image embeddings |
| **Augmentation** | Albumentations | Test-time augmentation |
| **Clustering** | HDBSCAN, scikit-learn | Image grouping |
| **Storage** | Cloudinary, Local FS | Image storage |
| **Database** | SQLite, PostgreSQL | Metadata storage |
| **Deployment** | AWS EC2/App Runner | Cloud hosting |
| **Infrastructure** | CloudFormation | IaC templates |

## Next Steps

1. ✅ **Completed**: Cloudinary integration, AWS deployment templates
2. ✅ **Completed**: Hierarchical clustering, category detection
3. ✅ **Completed**: Test-time augmentation for robustness
4. 🔄 **Future**: Background job processing for large batches
5. 🔄 **Future**: Semantic search using CLIP text encoder
6. 🔄 **Future**: User-defined tags and feedback system
7. 🔄 **Future**: Vector database for scalable similarity search
