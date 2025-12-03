# AWS Deployment Guide - AI Image Organizer

Complete guide for deploying to AWS free tier with Cloudinary integration.

## 📋 What's Included

✅ **Cloudinary Integration** - Cloud image storage  
✅ **AWS EC2 Template** - CloudFormation for EC2 deployment  
✅ **AWS App Runner Template** - Serverless deployment option  
✅ **Deployment Scripts** - Automated deployment  
✅ **Environment Configuration** - Production-ready settings  

## 🎯 Choose Your Deployment Method

**You only need ONE option, not both!**

- **Option 1: EC2** - More control, SSH access, manual management
- **Option 2: App Runner** - Serverless, automatic scaling, zero management

See `infrastructure/DEPLOYMENT-GUIDE.md` for detailed comparison.

## 🚀 Quick Start

### 1. Cloudinary Setup

1. Sign up at https://cloudinary.com (free tier: 25GB storage, 25GB bandwidth)
2. Get credentials from Dashboard > Settings
3. Add to `.env`:
   ```env
   USE_CLOUDINARY=true
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   ```

### 2. Choose ONE Deployment Method

**⚠️ Choose only ONE option below:**

#### Option A: EC2 (More Control) - Recommended for Learning
```bash
cd infrastructure
./deploy.sh
# Select option 1
```
- Full server control
- SSH access
- Manual management

#### Option B: App Runner (Serverless) - Recommended for Production
```bash
cd infrastructure
./deploy.sh
# Select option 2
```
- Zero server management
- Automatic scaling
- Built-in HTTPS

**💡 Tip**: If unsure, start with Option 1 (EC2) for learning, then switch to Option 2 (App Runner) for production.

## 📁 Infrastructure Files

- `infrastructure/cloudformation-template.yaml` - EC2 deployment
- `infrastructure/apprunner-template.yaml` - App Runner deployment
- `infrastructure/deploy.sh` - Automated deployment script
- `infrastructure/.env.example` - Environment variables template
- `infrastructure/README.md` - Detailed deployment guide

## 🔧 Configuration

### Environment Variables

Copy `infrastructure/.env.example` to `.env` and configure:

```env
# Cloudinary (Required for cloud storage)
USE_CLOUDINARY=true
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Database
DATABASE_URL=sqlite+aiosqlite:///./image_organizer.db

# CLIP Model
CLIP_DEVICE=cpu
CLIP_USE_AUGMENTATION=true
CLIP_NUM_AUGMENTATIONS=3

# Clustering
CLUSTERING_METHOD=hdbscan
```

## 💰 Free Tier Limits

### AWS
- **EC2 t2.micro**: 750 hours/month (1 year)
- **App Runner**: 750 hours/month
- **Data Transfer**: 15 GB out/month
- **EBS Storage**: 30 GB (1 year)

### Cloudinary
- **Storage**: 25 GB
- **Bandwidth**: 25 GB/month
- **Transformations**: Unlimited

## 📝 Deployment Steps

### EC2 Deployment

1. **Create Key Pair**:
   ```bash
   aws ec2 create-key-pair --key-name my-key --query 'KeyMaterial' --output text > my-key.pem
   chmod 400 my-key.pem
   ```

2. **Update AMI ID** in `cloudformation-template.yaml` for your region

3. **Deploy**:
   ```bash
   ./infrastructure/deploy.sh
   ```

4. **SSH and Configure**:
   ```bash
   ssh -i my-key.pem ec2-user@<PUBLIC_IP>
   cd /home/ec2-user/image-organizer
   nano .env  # Add Cloudinary credentials
   sudo systemctl restart image-organizer
   ```

### App Runner Deployment

1. **Create GitHub Connection** in AWS Console
2. **Deploy**:
   ```bash
   ./infrastructure/deploy.sh
   # Select option 2
   ```
3. **Set Environment Variables** in AWS Console

## 🔍 Verification

1. **Health Check**: `http://<your-url>/health`
2. **API Docs**: `http://<your-url>/docs`
3. **Test UI**: `http://<your-url>/test.html`

## 🐛 Troubleshooting

See `infrastructure/README.md` for detailed troubleshooting guide.

## 📚 Next Steps

- Set up custom domain (Route 53)
- Add SSL certificate (ACM)
- Configure CloudFront CDN
- Set up monitoring (CloudWatch)

