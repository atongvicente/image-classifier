# EC2 Deployment - What Gets Installed Automatically

## ✅ Yes, Python Code is Installed Automatically!

When you deploy Option 1 (EC2), the CloudFormation template automatically:

### 1. **Installs System Dependencies**
- ✅ Python 3.11
- ✅ pip (Python package manager)
- ✅ Git (for cloning repository)
- ✅ System updates

### 2. **Installs Your Application Code**

**Two Methods Available:**

#### Method A: From Git Repository (Recommended)
- Clones your code from GitHub/GitLab
- Checks out specified branch
- Installs all Python dependencies from `requirements.txt`
- Sets up systemd service
- **Starts automatically**

#### Method B: Manual Upload
- Creates directory structure
- Installs basic dependencies
- You upload code manually via SCP/SFTP
- Then start the service

### 3. **Sets Up Service**
- ✅ Creates systemd service (`image-organizer.service`)
- ✅ Configures auto-restart on failure
- ✅ Enables service to start on boot
- ✅ Sets up environment variables

## 📋 What Happens Step-by-Step

```
1. EC2 Instance Starts
   ↓
2. UserData Script Runs:
   ├── Updates system packages
   ├── Installs Python 3.11 + pip + git
   ├── Clones your repository (or creates directory)
   ├── Creates virtual environment
   ├── Installs all dependencies from requirements.txt
   ├── Creates .env file template
   ├── Sets up systemd service
   └── Enables service (starts on boot)
   ↓
3. Application is Ready!
   (May need to configure .env file)
```

## 🔧 Configuration Needed After Deployment

Even though code is installed, you need to:

1. **Configure Environment Variables**:
   ```bash
   ssh -i your-key.pem ec2-user@<PUBLIC_IP>
   cd /home/ec2-user/image-organizer
   nano .env
   # Add Cloudinary credentials, etc.
   ```

2. **Restart Service** (if you changed .env):
   ```bash
   sudo systemctl restart image-organizer
   ```

3. **Check Status**:
   ```bash
   sudo systemctl status image-organizer
   ```

## 📝 Repository Setup

### Option 1: Use Git Repository (Easiest)

1. **Push your code to GitHub/GitLab**
2. **Update CloudFormation template**:
   ```yaml
   RepositoryUrl: https://github.com/yourusername/image-organizer.git
   Branch: main
   ```
3. **Deploy** - Code will be cloned automatically

### Option 2: Manual Upload (If no Git repo)

1. **Deploy EC2 instance** (it will create directory structure)
2. **Upload code via SCP**:
   ```bash
   scp -i your-key.pem -r . ec2-user@<PUBLIC_IP>:/home/ec2-user/image-organizer/
   ```
3. **SSH and start service**:
   ```bash
   ssh -i your-key.pem ec2-user@<PUBLIC_IP>
   cd /home/ec2-user/image-organizer
   sudo systemctl start image-organizer
   ```

## ✅ Verification

After deployment, verify everything is installed:

```bash
# SSH into instance
ssh -i your-key.pem ec2-user@<PUBLIC_IP>

# Check Python
python3.11 --version

# Check if code is there
ls -la /home/ec2-user/image-organizer/

# Check if dependencies are installed
source /home/ec2-user/image-organizer/venv/bin/activate
pip list | grep fastapi

# Check service status
sudo systemctl status image-organizer

# Check if app is running
curl http://localhost:8000/health
```

## 🎯 Summary

**Yes, everything is installed automatically!** You just need to:
1. Provide Git repository URL (or upload manually)
2. Configure `.env` file with Cloudinary credentials
3. Restart service if needed

The template handles all the installation work for you!

