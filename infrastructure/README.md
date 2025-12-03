# AWS Deployment Guide

> ⚠️ **IMPORTANT**: You need to choose **ONE** deployment option (EC2 OR App Runner), not both!

This guide explains how to deploy the AI Image Organizer to AWS using free tier resources.

## 🎯 Quick Decision Guide

**Choose Option 1 (EC2)** if:
- You want full control and SSH access
- You're learning AWS
- You need to customize the environment

**Choose Option 2 (App Runner)** if:
- You want zero server management
- You want automatic scaling and HTTPS
- You prefer simplicity

See [DEPLOYMENT-GUIDE.md](./DEPLOYMENT-GUIDE.md) for detailed comparison.

## Prerequisites

1. **AWS Account** with free tier eligibility
2. **AWS CLI** installed and configured
3. **Cloudinary Account** (free tier available)
4. **GitHub Repository** (for App Runner deployment)

## Option 1: EC2 Deployment (CloudFormation)

### ✅ What Gets Installed Automatically

**Yes!** The EC2 template automatically installs:
- ✅ Python 3.11 and all dependencies
- ✅ Your application code (from Git or manual upload)
- ✅ All Python packages from `requirements.txt`
- ✅ Systemd service for auto-start
- ✅ Environment setup

See [EC2-SETUP.md](./EC2-SETUP.md) for details.

### Steps

1. **Create EC2 Key Pair** (if you don't have one):
   ```bash
   aws ec2 create-key-pair --key-name my-key-pair --query 'KeyMaterial' --output text > my-key-pair.pem
   chmod 400 my-key-pair.pem
   ```

2. **Update AMI ID** in `cloudformation-template.yaml`:
   - Find Amazon Linux 2023 AMI for your region:
     ```bash
     aws ec2 describe-images \
       --owners amazon \
       --filters "Name=name,Values=al2023-ami-2023*" \
       --query 'Images[0].ImageId' \
       --region us-east-1
     ```
   - Update `ImageId` in the template

3. **Choose Code Deployment Method**:

   **Option A: From Git Repository (Recommended)**
   - Push your code to GitHub/GitLab
   - Update `RepositoryUrl` parameter in template
   - Code will be cloned automatically

   **Option B: Manual Upload**
   - Deploy instance first
   - Upload code via SCP after deployment

4. **Deploy Stack**:
   ```bash
   chmod +x infrastructure/deploy.sh
   ./infrastructure/deploy.sh
   # Select option 1
   ```

5. **Configure Environment Variables**:
   ```bash
   # SSH into instance
   ssh -i my-key-pair.pem ec2-user@<PUBLIC_IP>
   
   # Edit environment file
   cd /home/ec2-user/image-organizer
   nano .env
   # Add Cloudinary credentials and other settings
   
   # Restart service (if needed)
   sudo systemctl restart image-organizer
   ```

### Free Tier Eligibility

- **t2.micro**: 750 hours/month free (1 year)
- **Data Transfer**: 15 GB out free/month
- **Storage**: 30 GB EBS free (1 year)

## Option 2: AWS App Runner (Serverless)

### Steps

1. **Create GitHub Connection**:
   - Go to AWS Console > App Runner > Connections
   - Create new connection to GitHub
   - Authorize AWS to access your repository
   - Note the Connection ARN

2. **Deploy**:
   ```bash
   ./infrastructure/deploy.sh
   # Select option 2
   ```

3. **Configure Environment Variables**:
   - Go to AWS Console > App Runner > Your Service
   - Configuration > Environment variables
   - Add variables from `.env.example`

### Free Tier Eligibility

- **750 hours/month** of compute time
- **0.25 vCPU, 0.5 GB RAM** per instance
- Auto-scaling included

## Cloudinary Setup

1. **Sign up** at https://cloudinary.com (free tier available)

2. **Get Credentials**:
   - Dashboard > Settings > Product environment credentials
   - Copy: Cloud name, API Key, API Secret

3. **Configure**:
   ```env
   USE_CLOUDINARY=true
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   ```

## Database Options

### Development (SQLite)
- Already configured
- No additional setup needed

### Production (RDS PostgreSQL)
1. Create RDS PostgreSQL instance (free tier: db.t2.micro)
2. Update `DATABASE_URL` in environment variables
3. Install `asyncpg` driver:
   ```bash
   pip install asyncpg
   ```

## Monitoring

### CloudWatch Logs
- EC2: `/var/log/messages` or systemd journal
- App Runner: Automatic CloudWatch Logs integration

### Health Checks
- Endpoint: `http://<your-url>/health`
- Should return: `{"status": "ok"}`

## Cost Estimation (Free Tier)

### EC2 Option
- **Compute**: Free (t2.micro, 750 hrs/month)
- **Storage**: Free (30 GB EBS, 1 year)
- **Data Transfer**: Free (15 GB out/month)
- **Total**: $0/month (within free tier)

### App Runner Option
- **Compute**: Free (750 hrs/month)
- **Total**: $0/month (within free tier)

### Cloudinary
- **Free Tier**: 25 GB storage, 25 GB bandwidth/month
- **Total**: $0/month (within free tier)

## Troubleshooting

### EC2 Issues
```bash
# Check service status
sudo systemctl status image-organizer

# View logs
sudo journalctl -u image-organizer -f

# Restart service
sudo systemctl restart image-organizer
```

### App Runner Issues
- Check CloudWatch Logs in AWS Console
- Verify environment variables are set
- Check build logs for dependency issues

### Common Issues
1. **Port 8000 not accessible**: Check security group rules
2. **Model download fails**: Increase instance storage or use pre-downloaded model
3. **Memory issues**: Reduce `CLIP_NUM_AUGMENTATIONS` or use smaller model

## Security Best Practices

1. **Use IAM Roles** instead of access keys when possible
2. **Restrict Security Groups** to specific IPs
3. **Enable HTTPS** using Application Load Balancer + ACM certificate
4. **Rotate Secrets** regularly
5. **Use Secrets Manager** for sensitive data

## Next Steps

1. Set up custom domain (Route 53)
2. Add SSL certificate (ACM)
3. Set up CloudFront CDN
4. Configure auto-scaling
5. Set up monitoring and alerts

