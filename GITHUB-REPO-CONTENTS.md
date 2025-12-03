# GitHub Repository Contents for Deployment

## ✅ Files That MUST Be in GitHub

These files are required for the EC2 deployment to work:

### 1. **Python Application Code**
```
backend/
├── __init__.py
└── app/
    ├── __init__.py
    ├── main.py              ← FastAPI application
    ├── config.py            ← Configuration settings
    ├── database.py           ← Database setup
    ├── models.py             ← SQLModel models
    ├── schemas.py            ← Pydantic schemas
    ├── dependencies.py       ← FastAPI dependencies
    ├── routers/
    │   ├── __init__.py
    │   ├── images.py         ← Image endpoints
    │   └── clusters.py       ← Cluster endpoints
    └── services/
        ├── __init__.py
        ├── image_service.py  ← Business logic
        └── storage_service.py ← Storage abstraction
```

### 2. **ML Code**
```
ml/
├── __init__.py
├── clip_embedder.py         ← CLIP model wrapper
└── clusterer.py             ← Clustering algorithms
```

### 3. **Configuration Files**
```
requirements.txt             ← Python dependencies (REQUIRED!)
pyproject.toml              ← Optional but recommended
.env.example                ← Environment variables template
```

### 4. **Frontend (Optional but Recommended)**
```
test.html                   ← Web UI for testing
```

### 5. **Documentation (Optional)**
```
README.md                   ← Project documentation
docs/                       ← Architecture docs
DEPLOYMENT.md               ← Deployment guide
```

## ❌ Files That Should NOT Be in GitHub

These should be in `.gitignore`:

```
# Python
__pycache__/
*.py[cod]
*.so
*.dylib
.venv/
venv/
*.egg-info/
dist/
build/

# Environment
.env                        ← NEVER commit this!
.env.local

# Database
*.db
*.sqlite
*.sqlite3
image_organizer.db

# Storage
storage/                    ← User uploaded images
*.jpg
*.jpeg
*.png
*.webp
*.gif

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Model cache (optional - can be large)
.cache/
models/
*.pth
*.pt
```

## 📋 Complete Repository Structure

Here's what your GitHub repo should look like:

```
image-organizer/
├── .gitignore              ← Important!
├── README.md
├── requirements.txt        ← REQUIRED
├── pyproject.toml         ← Optional
├── .env.example           ← Template (not actual .env)
├── DEPLOYMENT.md
│
├── backend/
│   ├── __init__.py
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── database.py
│       ├── models.py
│       ├── schemas.py
│       ├── dependencies.py
│       ├── routers/
│       │   ├── __init__.py
│       │   ├── images.py
│       │   └── clusters.py
│       └── services/
│           ├── __init__.py
│           ├── image_service.py
│           └── storage_service.py
│
├── ml/
│   ├── __init__.py
│   ├── clip_embedder.py
│   └── clusterer.py
│
├── test.html              ← Optional but useful
│
├── docs/
│   ├── architecture.md
│   └── image_analysis_libraries.md
│
└── infrastructure/        ← Optional (deployment templates)
    ├── cloudformation-template.yaml
    ├── apprunner-template.yaml
    └── deploy.sh
```

## 🚀 Quick Checklist Before Pushing to GitHub

- [ ] All Python files in `backend/` and `ml/` are included
- [ ] `requirements.txt` is present and up-to-date
- [ ] `.gitignore` is configured (excludes `.env`, `storage/`, `*.db`)
- [ ] `.env.example` is included (template, not actual secrets)
- [ ] `README.md` exists with setup instructions
- [ ] No sensitive data in code (API keys, passwords)
- [ ] No large files (models, images) - they'll be downloaded on EC2
- [ ] `test.html` is included (for web UI)

## ⚠️ Important Notes

### 1. **Never Commit These:**
- `.env` file (contains secrets)
- `storage/` directory (user uploads)
- `*.db` files (database files)
- `.venv/` (virtual environment)

### 2. **What Gets Downloaded on EC2:**
- CLIP model weights (~150MB) - downloaded automatically by transformers
- Python packages - installed from `requirements.txt`

### 3. **Environment Variables:**
- Store in `.env` file on EC2 (not in GitHub)
- Use `.env.example` as template in repo
- Set via SSH after deployment

## 📝 Example .gitignore

Make sure your `.gitignore` includes:

```gitignore
# Python
__pycache__/
*.py[cod]
*.so
.venv/
venv/

# Environment
.env
.env.local

# Database
*.db
*.sqlite

# Storage
storage/

# IDE
.vscode/
.idea/

# OS
.DS_Store

# Logs
*.log
```

## ✅ Verification

Before pushing to GitHub, verify:

```bash
# Check what will be committed
git status

# Make sure .env is not tracked
git check-ignore .env
# Should output: .env

# Make sure storage/ is not tracked
git check-ignore storage/
# Should output: storage/
```

## 🎯 Summary

**Minimum Required Files:**
1. ✅ All Python code (`backend/`, `ml/`)
2. ✅ `requirements.txt`
3. ✅ `.gitignore`
4. ✅ `.env.example` (template)

**Everything else is optional but recommended!**

