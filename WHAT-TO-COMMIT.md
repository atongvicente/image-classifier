# What Files to Commit to GitHub

## ✅ MUST Include (Required for Deployment)

### 1. **All Python Application Code**
```
backend/
├── __init__.py
└── app/
    ├── __init__.py
    ├── main.py              ✅ FastAPI app
    ├── config.py             ✅ Settings
    ├── database.py           ✅ DB setup
    ├── models.py             ✅ Data models
    ├── schemas.py            ✅ API schemas
    ├── dependencies.py       ✅ Dependencies
    ├── routers/
    │   ├── __init__.py
    │   ├── images.py         ✅ Image endpoints
    │   └── clusters.py       ✅ Cluster endpoints
    └── services/
        ├── __init__.py
        ├── image_service.py  ✅ Business logic
        └── storage_service.py ✅ Storage service
```

### 2. **ML Code**
```
ml/
├── __init__.py
├── clip_embedder.py          ✅ CLIP embedding
└── clusterer.py              ✅ Clustering
```

### 3. **Configuration Files**
```
requirements.txt              ✅ REQUIRED! Python dependencies
pyproject.toml                ✅ Project metadata
.env.example                  ✅ Environment template (NOT .env!)
```

### 4. **Frontend**
```
test.html                     ✅ Web UI
```

### 5. **Documentation** (Recommended)
```
README.md                     ✅ Project docs
DEPLOYMENT.md                 ✅ Deployment guide
docs/                         ✅ Architecture docs
```

### 6. **Infrastructure** (Optional but Useful)
```
infrastructure/
├── cloudformation-template.yaml
├── apprunner-template.yaml
├── deploy.sh
└── README.md
```

### 7. **Scripts**
```
run.sh                        ✅ Local run script
```

### 8. **Git Configuration**
```
.gitignore                    ✅ IMPORTANT! Excludes sensitive files
```

## ❌ DO NOT Include (Already in .gitignore)

These files are automatically excluded:

```
.env                          ❌ Contains secrets (Cloudinary keys, etc.)
storage/                      ❌ User uploaded images
*.db                          ❌ Database files
.venv/                        ❌ Virtual environment
__pycache__/                  ❌ Python cache
*.pyc                         ❌ Compiled Python
uv.lock                       ❌ Lock file (optional)
```

## 📋 Complete File Checklist

Here's exactly what should be in your GitHub repo:

```
image-organizer/
├── .gitignore                ✅
├── README.md                 ✅
├── requirements.txt          ✅ REQUIRED
├── pyproject.toml            ✅
├── .env.example              ✅ (template, not actual .env)
├── DEPLOYMENT.md             ✅
├── run.sh                    ✅
│
├── backend/                  ✅ ALL Python files
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
├── ml/                       ✅ ALL Python files
│   ├── __init__.py
│   ├── clip_embedder.py
│   └── clusterer.py
│
├── test.html                 ✅
│
├── docs/                     ✅
│   ├── architecture.md
│   ├── architecture-diagram.md
│   └── image_analysis_libraries.md
│
└── infrastructure/           ✅ (optional)
    ├── cloudformation-template.yaml
    ├── apprunner-template.yaml
    ├── deploy.sh
    └── README.md
```

## 🚀 Quick Git Commands

### Check What Will Be Committed:
```bash
git status
```

### Add All Required Files:
```bash
# Add everything except what's in .gitignore
git add .

# Verify what's staged
git status
```

### Verify Sensitive Files Are Excluded:
```bash
# These should NOT appear in git status:
git check-ignore .env storage/ image_organizer.db .venv/
# Should output the file paths (meaning they're ignored)
```

## ⚠️ Critical: Never Commit These!

1. **`.env`** - Contains Cloudinary API keys and secrets
2. **`storage/`** - User uploaded images (can be large)
3. **`*.db`** - Database files (contain data)
4. **`.venv/`** - Virtual environment (can be recreated)

## ✅ Pre-Commit Checklist

Before pushing to GitHub:

- [ ] All Python files in `backend/` and `ml/` are included
- [ ] `requirements.txt` is present and complete
- [ ] `.gitignore` is configured correctly
- [ ] `.env` is NOT tracked (check with `git status`)
- [ ] `storage/` directory is NOT tracked
- [ ] `*.db` files are NOT tracked
- [ ] `.env.example` exists (template for others)
- [ ] `README.md` has setup instructions

## 📝 Example: What EC2 Will See After Clone

When EC2 clones your repo, it will get:

```
/home/ec2-user/image-organizer/
├── backend/          ← All Python code
├── ml/               ← ML code
├── requirements.txt  ← Dependencies
├── test.html        ← Frontend
└── .env.example      ← Template
```

Then EC2 will:
1. Create `.env` file (you configure this via SSH)
2. Create `storage/` directory (for local storage if not using Cloudinary)
3. Create `venv/` (virtual environment)
4. Install dependencies from `requirements.txt`

## 🎯 Summary

**Minimum Required:**
- ✅ All `.py` files in `backend/` and `ml/`
- ✅ `requirements.txt`
- ✅ `.gitignore`

**Everything else is recommended but optional!**

