# AI Image Organizer - Visual Architecture Diagram

## Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Web Browser (test.html)                                               │  │
│  │  • Drag & Drop Image Upload                                            │  │
│  │  • Hierarchical Cluster Visualization                                  │  │
│  │  • Category Filtering (Object + Background)                             │  │
│  │  • Image Gallery with Metadata                                         │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/REST API
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FASTAPI BACKEND SERVER                               │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  API Endpoints                                                         │  │
│  │  • POST /images          → Upload & Classify                           │  │
│  │  • GET  /images          → List all images                             │  │
│  │  • GET  /clusters        → Flat cluster list                           │  │
│  │  • GET  /clusters/grouped → Hierarchical clusters                     │  │
│  │  • GET  /health          → Health check                               │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
┌───────────────────────────────────┐  ┌───────────────────────────────────┐
│      ML PROCESSING PIPELINE        │  │      STORAGE SERVICE               │
│                                    │  │                                    │
│  ┌──────────────────────────────┐ │  │  ┌──────────────────────────────┐ │
│  │  Image Input                 │ │  │  │  Storage Abstraction         │ │
│  └──────────────┬───────────────┘ │  │  │  (StorageService Interface)  │ │
│                 │                  │  │  └──────────────┬───────────────┘ │
│                 ▼                  │  │                 │                 │
│  ┌──────────────────────────────┐ │  │     ┌───────────┴───────────┐    │
│  │  Test-Time Augmentation      │ │  │     │                       │    │
│  │  (Albumentations)            │ │  │     ▼                       ▼    │
│  │  • Horizontal Flip           │ │  │  ┌──────────┐      ┌──────────┐ │
│  │  • Brightness/Contrast       │ │  │  │Cloudinary│      │  Local   │ │
│  │  • Gamma Correction          │ │  │  │  Cloud   │      │Filesystem│ │
│  │  • CLAHE                     │ │  │  │          │      │          │ │
│  │  • Gaussian Noise            │ │  │  │ • CDN    │      │ • /storage│ │
│  │  → 3 Augmented Views         │ │  │  │ • Transform│     │ • Static │ │
│  └──────────────┬───────────────┘ │  │  │ • 25GB Free│     │   serving│ │
│                 │                  │  │  └──────────┘      └──────────┘ │
│                 ▼                  │  └───────────────────────────────────┘
│  ┌──────────────────────────────┐ │
│  │  CLIP Model                  │ │
│  │  (openai/clip-vit-base-      │ │
│  │   patch32)                   │ │
│  │  • Extract embeddings        │ │
│  │  • Average across augments   │ │
│  │  → 512-dim vector            │ │
│  └──────────────┬───────────────┘ │
│                 │                  │
│                 ▼                  │
│  ┌──────────────────────────────┐ │
│  │  Classification              │ │
│  │  • Object Category           │ │
│  │    (cat, dog, car, etc.)     │ │
│  │  • Background Category       │ │
│  │    (indoor, outdoor, etc.)   │ │
│  └──────────────┬───────────────┘ │
│                 │                  │
│                 ▼                  │
│  ┌──────────────────────────────┐ │
│  │  Clustering                  │ │
│  │  • HDBSCAN (primary)         │ │
│  │  • MiniBatchKMeans (alt)     │ │
│  │  → Hierarchical Groups       │ │
│  └──────────────────────────────┘ │
└───────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATABASE LAYER                                    │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  SQLite (Dev) / PostgreSQL (Prod)                                    │  │
│  │  • Image Metadata (filename, size, dimensions)                        │  │
│  │  • CLIP Embeddings (512-dim binary)                                   │  │
│  │  • Object Category                                                    │  │
│  │  • Background Category                                                │  │
│  │  • Storage Path (Cloudinary public_id or file path)                   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        AWS DEPLOYMENT INFRASTRUCTURE                         │
│                                                                              │
│  ┌──────────────────────────────┐  ┌──────────────────────────────┐        │
│  │  Option 1: EC2                │  │  Option 2: App Runner         │        │
│  │                              │  │                              │        │
│  │  ┌────────────────────────┐  │  │  ┌────────────────────────┐  │        │
│  │  │  VPC                   │  │  │  │  GitHub Connection     │  │        │
│  │  │  • Public Subnet       │  │  │  │  • Auto Deploy          │  │        │
│  │  │  • Internet Gateway    │  │  │  │  • Auto Scaling         │  │        │
│  │  └────────────────────────┘  │  │  │  • HTTPS Included       │  │        │
│  │  ┌────────────────────────┐  │  │  └────────────────────────┘  │        │
│  │  │  Security Group        │  │  │  ┌────────────────────────┐  │        │
│  │  │  • Port 8000 (API)     │  │  │  │  Container Service     │  │        │
│  │  │  • Port 22 (SSH)       │  │  │  │  • 0.25 vCPU            │  │        │
│  │  │  • Port 80/443 (HTTP)  │  │  │  │  • 0.5 GB RAM           │  │        │
│  │  └────────────────────────┘  │  │  └────────────────────────┘  │        │
│  │  ┌────────────────────────┐  │  │                              │        │
│  │  │  EC2 Instance          │  │  │  Free Tier: 750 hrs/month   │        │
│  │  │  • t2.micro            │  │  │                              │        │
│  │  │  • Systemd Service     │  │  │                              │        │
│  │  │  • Auto-restart        │  │  │                              │        │
│  │  └────────────────────────┘  │  │                              │        │
│  │  ┌────────────────────────┐  │  │                              │        │
│  │  │  Elastic IP            │  │  │                              │        │
│  │  │  (Static IP Address)   │  │  │                              │        │
│  │  └────────────────────────┘  │  │                              │        │
│  │                              │  │                              │        │
│  │  Free Tier: 750 hrs/month    │  │                              │        │
│  └──────────────────────────────┘  └──────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Visualization

### Upload & Classification Flow
```
User Uploads Image
        │
        ▼
┌───────────────────┐
│  FastAPI Receives │
│  multipart/form   │
└─────────┬─────────┘
          │
          ├─────────────────┐
          │                 │
          ▼                 ▼
┌─────────────────┐  ┌──────────────┐
│ Upload to       │  │ Process with │
│ Storage         │  │ ML Pipeline  │
│                 │  │              │
│ Cloudinary ────┐│  │ 1. Augment   │
│ or Local ─────┐││  │    (3 views) │
└────────────────┘││  │ 2. CLIP      │
                  ││  │    (embedd)  │
                  ││  │ 3. Classify   │
                  ││  │    (object + │
                  ││  │     bg)      │
                  ││  └──────┬───────┘
                  ││         │
                  ││         ▼
                  ││  ┌──────────────┐
                  ││  │ Save to DB   │
                  ││  │ • Metadata   │
                  ││  │ • Embedding  │
                  ││  │ • Categories │
                  ││  └──────────────┘
                  ││
                  └┴─────────┐
                             ▼
                    ┌─────────────────┐
                    │ Return Response │
                    │ with image_url  │
                    └─────────────────┘
```

### Clustering Flow
```
GET /clusters/grouped Request
        │
        ▼
┌──────────────────────┐
│ Retrieve All Images  │
│ from Database        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Group by Object      │
│ • cat → [images]     │
│ • dog → [images]     │
│ • car → [images]     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ For each object,     │
│ group by background │
│ • cat-indoor → [imgs]│
│ • cat-outdoor → [imgs]│
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Apply HDBSCAN        │
│ (if multiple images) │
│ • Find sub-clusters  │
│ • Handle outliers    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Return Hierarchical  │
│ Structure            │
│ {                    │
│   "cat": {           │
│     "indoor": [...], │
│     "outdoor": [...] │
│   }                  │
│ }                    │
└──────────────────────┘
```

## Technology Stack Visualization

```
┌─────────────────────────────────────────────────────────┐
│                    TECHNOLOGY STACK                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Frontend:        HTML5, CSS3, JavaScript (Vanilla)    │
│  Backend:         FastAPI, Uvicorn, Python 3.12         │
│  ML Framework:    PyTorch, Transformers (Hugging Face)  │
│  ML Model:        CLIP (OpenAI)                         │
│  Augmentation:    Albumentations                        │
│  Clustering:      HDBSCAN, scikit-learn                 │
│  Storage:         Cloudinary, Local Filesystem          │
│  Database:        SQLite, PostgreSQL (async)            │
│  ORM:             SQLModel                              │
│  Cloud:           AWS (EC2, App Runner)                  │
│  Infrastructure:  CloudFormation                        │
│  Deployment:      GitHub, Systemd                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Component Interaction Diagram

```
┌──────────┐
│  User    │
└────┬─────┘
     │
     │ 1. Upload Image
     ▼
┌─────────────────┐
│  FastAPI        │
│  Router         │
└────┬────────────┘
     │
     ├──→ ImageService
     │    ├──→ StorageService (Cloudinary/Local)
     │    ├──→ ClipEmbedder
     │    │    ├──→ Augmentation
     │    │    └──→ CLIP Model
     │    └──→ Database (SQLModel)
     │
     └──→ ClusterService
          ├──→ Database (get embeddings)
          └──→ Clusterer (HDBSCAN/KMeans)
               └──→ Return grouped clusters
```

