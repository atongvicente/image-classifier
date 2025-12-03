# Image Analysis Libraries Used

This document details all the libraries used for image analysis and processing in the AI Image Organizer.

## Core Image Processing Libraries

### 1. **Pillow (PIL)** - `Pillow==10.3.0`
**Purpose:** Basic image loading, manipulation, and format conversion
- **Used for:**
  - Loading images from bytes: `Image.open(BytesIO(data))`
  - Converting images to RGB format
  - Getting image dimensions (width, height)
- **Location:** `backend/app/services/image_service.py`, `ml/clip_embedder.py`

### 2. **OpenCV (cv2)** - `opencv-python-headless==4.12.0.88`
**Purpose:** Computer vision operations (used by Albumentations)
- **Used for:**
  - Image processing operations under the hood
  - Required dependency for Albumentations library
- **Note:** Using `opencv-python-headless` (no GUI dependencies) for server environments

## Deep Learning & Vision Models

### 3. **PyTorch (torch)** - `torch==2.3.0`
**Purpose:** Deep learning framework for running neural networks
- **Used for:**
  - Running CLIP model inference
  - Tensor operations and GPU/CPU computation
  - Model feature extraction
- **Location:** `ml/clip_embedder.py`

### 4. **Transformers (Hugging Face)** - `transformers==4.41.2`
**Purpose:** Pre-trained model loading and inference
- **Used for:**
  - Loading CLIP model: `CLIPModel.from_pretrained()`
  - CLIP processor for image/text encoding: `CLIPProcessor`
  - Extracting image features: `get_image_features()`
  - Extracting text features: `get_text_features()`
- **Model:** `openai/clip-vit-base-patch32`
- **Location:** `ml/clip_embedder.py`

## Image Augmentation

### 5. **Albumentations** - `albumentations==1.4.21`
**Purpose:** Advanced image augmentation for test-time augmentation (TTA)
- **Used for:**
  - **HorizontalFlip** (p=0.5): Randomly flip images horizontally
  - **RandomBrightnessContrast** (p=0.5): Adjust brightness and contrast
  - **RandomGamma** (p=0.3): Gamma correction for lighting variations
  - **CLAHE** (p=0.3): Contrast Limited Adaptive Histogram Equalization
  - **GaussNoise** (p=0.2): Add Gaussian noise for robustness
- **Purpose:** Create multiple augmented views of images to improve classification accuracy
- **Location:** `ml/clip_embedder.py`

## Numerical Computing

### 6. **NumPy** - `numpy==2.2.6`
**Purpose:** Numerical operations on image embeddings and arrays
- **Used for:**
  - Converting image data to arrays: `np.array(pil_image)`
  - Embedding vector operations: `np.vstack()`, `np.mean()`
  - Array manipulation for clustering
- **Location:** Throughout `ml/` directory

## Clustering & Analysis

### 7. **scikit-learn** - `scikit-learn==1.4.2`
**Purpose:** Machine learning algorithms for clustering
- **Used for:**
  - **MiniBatchKMeans**: Fast K-means clustering algorithm
  - Alternative clustering method (when not using HDBSCAN)
- **Location:** `ml/clusterer.py`

### 8. **HDBSCAN** - `hdbscan==0.8.33`
**Purpose:** Density-based clustering algorithm
- **Used for:**
  - Automatic cluster detection (no need to specify number of clusters)
  - Finding clusters of varying densities
  - Identifying noise/outlier points
- **Advantages:**
  - Automatically determines optimal number of clusters
  - Better at finding natural groupings
  - Handles irregular cluster shapes
- **Location:** `ml/clusterer.py`

## Image Analysis Pipeline

### Complete Flow:

1. **Image Loading** (Pillow)
   ```
   PIL Image → RGB conversion → Dimension extraction
   ```

2. **Image Augmentation** (Albumentations + OpenCV)
   ```
   Original Image → [Augmented versions] → Multiple views
   ```

3. **Feature Extraction** (Transformers + PyTorch)
   ```
   Images → CLIP Model → Embedding vectors (512-dim)
   ```

4. **Classification** (Transformers + PyTorch)
   ```
   Image embeddings + Text prompts → Similarity scores → Category labels
   ```

5. **Clustering** (HDBSCAN/scikit-learn + NumPy)
   ```
   Embeddings → Clustering algorithm → Group assignments
   ```

## Library Dependencies

```
Pillow (image I/O)
    ↓
Albumentations (augmentation)
    ↓
OpenCV (image processing)
    ↓
Transformers (CLIP model)
    ↓
PyTorch (neural network execution)
    ↓
NumPy (array operations)
    ↓
HDBSCAN/scikit-learn (clustering)
```

## Configuration

All libraries can be configured via environment variables in `.env`:

```env
# CLIP Model
CLIP_MODEL_NAME=openai/clip-vit-base-patch32
CLIP_DEVICE=cpu
CLIP_USE_AUGMENTATION=true
CLIP_NUM_AUGMENTATIONS=3

# Clustering
CLUSTERING_METHOD=hdbscan  # or "kmeans"
HDBSCAN_MIN_CLUSTER_SIZE=2
```

## Performance Notes

- **CPU vs GPU:** Currently using CPU (`CLIP_DEVICE=cpu`). For faster processing, set to `cuda` if GPU available
- **Augmentation:** Increases processing time by ~3x (default 3 augmentations) but improves accuracy
- **HDBSCAN:** Slower than KMeans but provides better cluster quality

