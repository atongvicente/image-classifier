# Where the Repository is Cloned - Explained

## 📍 Location in CloudFormation Template

The Git repository cloning happens in the **UserData script** section of the CloudFormation template.

### Exact Location

**File**: `infrastructure/cloudformation-template.yaml`  
**Section**: `EC2Instance` → `UserData` → Lines 168-175

### The Code

```yaml
UserData:
  Fn::Base64: !Sub |
    #!/bin/bash
    set -e
    
    # ... (system updates and package installation) ...
    
    # Install application
    cd /home/ec2-user
    
    # ⬇️ HERE IS WHERE THE CLONING HAPPENS ⬇️
    # Method 1: Clone from Git (if RepositoryUrl parameter is provided)
    if [ -n "${RepositoryUrl}" ] && [ "${RepositoryUrl}" != "none" ]; then
      echo "Cloning from Git repository: ${RepositoryUrl}"
      git clone ${RepositoryUrl} image-organizer || true    # ← CLONE COMMAND
      cd image-organizer
      if [ -n "${Branch}" ] && [ "${Branch}" != "main" ]; then
        git checkout ${Branch}                              # ← CHECKOUT BRANCH
      fi
    else
      # Method 2: Create directory structure (manual upload required)
      echo "Creating directory structure. You'll need to upload code manually."
      mkdir -p image-organizer
      cd image-organizer
    fi
    # ⬆️ END OF CLONING SECTION ⬆️
    
    # ... (rest of installation: venv, pip install, systemd service) ...
```

## 🔍 Step-by-Step Explanation

### 1. **Check if Repository URL is Provided**
```bash
if [ -n "${RepositoryUrl}" ] && [ "${RepositoryUrl}" != "none" ]; then
```
- Checks if `RepositoryUrl` parameter has a value
- Skips if it's empty or set to "none"

### 2. **Clone the Repository**
```bash
git clone ${RepositoryUrl} image-organizer || true
```
- **Command**: `git clone <your-repo-url> image-organizer`
- **Location**: Clones into `/home/ec2-user/image-organizer`
- **`|| true`**: Continues even if clone fails (prevents script from stopping)

### 3. **Checkout Specific Branch** (if not main)
```bash
if [ -n "${Branch}" ] && [ "${Branch}" != "main" ]; then
  git checkout ${Branch}
fi
```
- Switches to the specified branch
- Defaults to `main` if not specified

## 📝 How to Use It

### When Deploying, Provide Repository URL:

**Option 1: Via deploy.sh script**
```bash
./infrastructure/deploy.sh
# When prompted, provide your GitHub URL
```

**Option 2: Direct CloudFormation**
```bash
aws cloudformation create-stack \
  --stack-name my-stack \
  --template-body file://infrastructure/cloudformation-template.yaml \
  --parameters \
    ParameterKey=RepositoryUrl,ParameterValue=https://github.com/yourusername/image-organizer.git \
    ParameterKey=Branch,ParameterValue=main \
    ParameterKey=KeyPairName,ParameterValue=my-key
```

**Option 3: Update Template Default**
Edit `cloudformation-template.yaml`:
```yaml
RepositoryUrl:
  Type: String
  Default: https://github.com/yourusername/image-organizer.git  # ← Add your URL here
  Description: Git repository URL to clone
```

## 🎯 Example Flow

```
1. EC2 Instance Starts
   ↓
2. UserData Script Executes:
   ├── Installs Python, Git, etc.
   ├── Changes to /home/ec2-user
   ├── Checks: Is RepositoryUrl provided?
   │   ├── YES → git clone https://github.com/user/repo.git image-organizer
   │   │         → cd image-organizer
   │   │         → git checkout main (or specified branch)
   │   └── NO  → mkdir image-organizer (manual upload needed)
   ├── Creates virtual environment
   ├── Installs dependencies
   └── Sets up systemd service
   ↓
3. Code is Ready!
```

## 🔧 Testing the Clone Manually

If you SSH into the instance, you can see the cloned code:

```bash
ssh -i your-key.pem ec2-user@<PUBLIC_IP>
cd /home/ec2-user/image-organizer
ls -la  # Should show your project files
git remote -v  # Shows the repository URL
```

## ⚠️ Important Notes

1. **Repository Must Be Public** (or use SSH keys for private repos)
2. **Git Must Be Installed** (done automatically in the script)
3. **Branch Defaults to 'main'** if not specified
4. **Clone Happens on First Boot** - UserData runs once when instance starts

## 🐛 Troubleshooting

If clone fails:
1. Check repository URL is correct
2. Verify repository is accessible (public or has access)
3. Check CloudWatch logs: `/var/log/cloud-init-output.log`
4. SSH and run manually: `git clone <url> image-organizer`

