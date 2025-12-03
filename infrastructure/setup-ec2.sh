#!/bin/bash
# Quick setup script to run on EC2 after deployment
# Usage: Copy this to EC2 and run: bash setup-ec2.sh

set -e

echo "🔧 Setting up AI Image Organizer on EC2..."

cd /home/ec2-user/image-organizer

# Check if .env already exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists. Backing up..."
    cp .env .env.backup
fi

# Create .env file with template
cat > .env << 'EOF'
# Cloudinary Configuration (REQUIRED - update with your credentials)
USE_CLOUDINARY=false
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Database
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
EOF

echo "✅ Created .env file template"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env file: nano .env"
echo "2. Add your Cloudinary credentials:"
echo "   - CLOUDINARY_CLOUD_NAME=your_actual_cloud_name"
echo "   - CLOUDINARY_API_KEY=your_actual_api_key"
echo "   - CLOUDINARY_API_SECRET=your_actual_api_secret"
echo "   - USE_CLOUDINARY=true"
echo ""
echo "3. Create storage directory (if not using Cloudinary):"
echo "   mkdir -p storage"
echo ""
echo "4. Restart service:"
echo "   sudo systemctl restart image-organizer"
echo ""
echo "5. Check status:"
echo "   sudo systemctl status image-organizer"

