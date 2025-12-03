# EC2 Configuration - Setting Up Required Files

## Overview

After EC2 deployment, these files need to be created/configured on the server:
- `.env` - Environment variables (Cloudinary keys, etc.)
- `storage/` - Directory for local storage (if not using Cloudinary)
- `*.db` - Database file (created automatically)
- `.venv/` - Virtual environment (created automatically)

## Step-by-Step Setup Guide

### 1. SSH into Your EC2 Instance

```bash
ssh -i your-key.pem ec2-user@<PUBLIC_IP>
```

### 2. Navigate to Application Directory

```bash
cd /home/ec2-user/image-organizer
```

### 3. Create `.env` File (REQUIRED)

This is the most important step - configure your environment variables:

```bash
nano .env
```

**Add these configurations:**

```env
# Cloudinary Configuration (REQUIRED for cloud storage)
USE_CLOUDINARY=true
CLOUDINARY_CLOUD_NAME=your_cloud_name_here
CLOUDINARY_API_KEY=your_api_key_here
CLOUDINARY_API_SECRET=your_api_secret_here

# Database (SQLite - created automatically)
DATABASE_URL=sqlite+aiosqlite:///./image_organizer.db

# CLIP Settings
CLIP_MODEL_NAME=openai/clip-vit-base-patch32
CLIP_DEVICE=cpu
CLIP_USE_AUGMENTATION=true
CLIP_NUM_AUGMENTATIONS=3

# Clustering
CLUSTERING_METHOD=hdbscan
HDBSCAN_MIN_CLUSTER_SIZE=2

# Application
APP_NAME=AI Image Organizer
```

**Save and exit:**
- Press `Ctrl+X`
- Press `Y` to confirm
- Press `Enter` to save

### 4. Create `storage/` Directory (If Using Local Storage)

```bash
# Only needed if USE_CLOUDINARY=false
mkdir -p storage
chmod 755 storage
```

**Note:** If `USE_CLOUDINARY=true`, this directory is optional (Cloudinary handles storage).

### 5. Verify Virtual Environment (`.venv/`)

The deployment script should have created this automatically, but verify:

```bash
# Check if venv exists
ls -la venv/

# If it doesn't exist, create it:
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 6. Database File (`*.db`)

**This is created automatically** when the application first runs. No manual setup needed!

The database will be created at:
```
/home/ec2-user/image-organizer/image_organizer.db
```

### 7. Restart the Service

After configuring `.env`, restart the service:

```bash
sudo systemctl restart image-organizer
```

### 8. Check Service Status

```bash
# Check if service is running
sudo systemctl status image-organizer

# View logs if there are issues
sudo journalctl -u image-organizer -f
```

## Complete Setup Script

Here's a complete script you can run on EC2:

```bash
#!/bin/bash
# Run this on EC2 after deployment

cd /home/ec2-user/image-organizer

# 1. Create .env file
cat > .env << 'EOF'
USE_CLOUDINARY=true
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
DATABASE_URL=sqlite+aiosqlite:///./image_organizer.db
CLIP_DEVICE=cpu
CLUSTERING_METHOD=hdbscan
EOF

# 2. Edit .env with your actual Cloudinary credentials
nano .env

# 3. Create storage directory (if needed)
mkdir -p storage

# 4. Restart service
sudo systemctl restart image-organizer

# 5. Check status
sudo systemctl status image-organizer
```

## File Locations on EC2

After setup, your files will be at:

```
/home/ec2-user/image-organizer/
├── .env                    ← You create this (with Cloudinary keys)
├── storage/                ← Created automatically or manually
├── image_organizer.db      ← Created automatically on first run
├── .venv/                  ← Created by deployment script
├── backend/                ← Cloned from GitHub
├── ml/                     ← Cloned from GitHub
└── requirements.txt        ← Cloned from GitHub
```

## Quick Reference

| File/Directory | Created By | When | Location |
|----------------|------------|------|----------|
| `.env` | **You** | After deployment | `/home/ec2-user/image-organizer/.env` |
| `storage/` | You or app | If local storage | `/home/ec2-user/image-organizer/storage/` |
| `*.db` | Application | First run | `/home/ec2-user/image-organizer/image_organizer.db` |
| `.venv/` | Deployment script | During deployment | `/home/ec2-user/image-organizer/.venv/` |

## Troubleshooting

### If `.env` is missing:
```bash
# Service will fail to start properly
# Create it as shown in step 3 above
```

### If `storage/` is missing:
```bash
# Only needed if USE_CLOUDINARY=false
mkdir -p storage
sudo systemctl restart image-organizer
```

### If database doesn't exist:
```bash
# It will be created automatically on first API call
# Or you can trigger it:
curl http://localhost:8000/health
```

### If `.venv/` is missing:
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart image-organizer
```

## Summary

**What you need to do manually:**
1. ✅ Create `.env` file with Cloudinary credentials
2. ✅ (Optional) Create `storage/` if not using Cloudinary

**What happens automatically:**
- ✅ `.venv/` - Created by deployment script
- ✅ `*.db` - Created when app first runs
- ✅ All Python code - Cloned from GitHub

**Most Important:** Just create the `.env` file with your Cloudinary credentials!

