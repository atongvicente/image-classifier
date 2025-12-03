# Quick Setup Guide - After EC2 Deployment

## What Gets Created Automatically ✅

These are created by the deployment script - **you don't need to do anything:**

- ✅ `.venv/` - Virtual environment (created automatically)
- ✅ `*.db` - Database file (created when app first runs)
- ✅ `storage/` - Directory (created by deployment script)

## What You Need to Set Up Manually 🔧

### 1. `.env` File (REQUIRED)

This is the **only thing you must configure manually** after deployment.

**Steps:**

```bash
# 1. SSH into EC2
ssh -i your-key.pem ec2-user@<PUBLIC_IP>

# 2. Go to application directory
cd /home/ec2-user/image-organizer

# 3. Create/edit .env file
nano .env
```

**Add your Cloudinary credentials:**

```env
USE_CLOUDINARY=true
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

DATABASE_URL=sqlite+aiosqlite:///./image_organizer.db
CLIP_DEVICE=cpu
CLUSTERING_METHOD=hdbscan
```

**Save:** `Ctrl+X`, then `Y`, then `Enter`

**Restart service:**
```bash
sudo systemctl restart image-organizer
```

## Complete Setup Process

### Step 1: Deploy EC2 Instance
```bash
./infrastructure/deploy.sh
# Select option 1
```

### Step 2: Wait for Deployment
- EC2 instance starts
- Code is cloned from GitHub
- Dependencies are installed
- Service is set up (but not started yet)

### Step 3: Configure .env (5 minutes)
```bash
# SSH into instance
ssh -i your-key.pem ec2-user@<PUBLIC_IP>

# Create .env with your Cloudinary credentials
cd /home/ec2-user/image-organizer
nano .env
# (Add your Cloudinary keys as shown above)

# Restart service
sudo systemctl restart image-organizer
```

### Step 4: Verify It Works
```bash
# Check service status
sudo systemctl status image-organizer

# Test the API
curl http://localhost:8000/health
# Should return: {"status":"ok"}
```

## File Status After Deployment

| File | Status | Action Needed |
|------|--------|---------------|
| `.env` | ❌ Missing | **YOU CREATE** with Cloudinary keys |
| `storage/` | ✅ Created | None (or create if missing) |
| `*.db` | ✅ Auto-created | None (created on first run) |
| `.venv/` | ✅ Created | None (created by script) |

## Summary

**You only need to:**
1. ✅ Create `.env` file
2. ✅ Add Cloudinary credentials to `.env`
3. ✅ Restart the service

**Everything else happens automatically!**

See [EC2-CONFIGURATION.md](./EC2-CONFIGURATION.md) for detailed instructions.

