# AWS IAM User Setup Guide

## Why Create an IAM User?

**Never use root account credentials for CLI access!** Root account has unlimited access and is a security risk. Create a dedicated IAM user with only the permissions needed.

## Step-by-Step: Create IAM User

### 1. Create the User

1. Go to **AWS Console** → **IAM** → **Users**
2. Click **"Create user"**
3. Enter username: `image-organizer-deploy` (or any name you prefer)
4. Click **"Next"**

### 2. Attach Permissions

**Option A: Use AWS Managed Policies (Easier, but broader permissions)**

Attach these managed policies:
- ✅ `CloudFormationFullAccess` - To deploy CloudFormation stacks
- ✅ `AmazonEC2FullAccess` - To create EC2 instances, VPCs, security groups, key pairs
- ✅ `IAMFullAccess` - To create IAM roles (needed for EC2 instance profiles)

**Option B: Custom Policy (More Secure, Minimal Permissions)**

Create a custom policy with only what's needed:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*",
        "ec2:*",
        "iam:CreateRole",
        "iam:DeleteRole",
        "iam:AttachRolePolicy",
        "iam:DetachRolePolicy",
        "iam:PutRolePolicy",
        "iam:DeleteRolePolicy",
        "iam:GetRole",
        "iam:GetRolePolicy",
        "iam:ListRolePolicies",
        "iam:ListAttachedRolePolicies",
        "iam:PassRole",
        "iam:CreateInstanceProfile",
        "iam:DeleteInstanceProfile",
        "iam:AddRoleToInstanceProfile",
        "iam:RemoveRoleFromInstanceProfile",
        "iam:GetInstanceProfile",
        "iam:ListInstanceProfilesForRole"
      ],
      "Resource": "*"
    }
  ]
}
```

**For App Runner deployment, also add:**
- `AppRunnerFullAccess` (if using App Runner option)

### 3. Create Access Key

1. After creating the user, click on the username
2. Go to **"Security credentials"** tab
3. Click **"Create access key"**
4. Select **"Command Line Interface (CLI)"**
5. Click **"Next"** → **"Create access key"**
6. **IMPORTANT**: Copy both:
   - **Access Key ID**
   - **Secret Access Key** (you can only see this once!)

### 4. Configure AWS CLI

Run this command and enter the credentials:

```bash
aws configure
```

Enter:
- **AWS Access Key ID**: (paste from step 3)
- **AWS Secret Access Key**: (paste from step 3)
- **Default region name**: `us-east-1` (or your preferred region)
- **Default output format**: `json` (or press Enter)

### 5. Verify Configuration

```bash
# Test your access
aws sts get-caller-identity

# Should show your IAM user ARN, not root account
```

## Required Permissions Breakdown

### For EC2 Deployment (CloudFormation):
- **CloudFormation**: Create/update/delete stacks
- **EC2**: Create instances, VPCs, subnets, security groups, key pairs, elastic IPs
- **IAM**: Create roles and instance profiles for EC2

### For App Runner Deployment:
- **CloudFormation**: Create/update/delete stacks
- **App Runner**: Create/update services
- **IAM**: Create service roles for App Runner

## Security Best Practices

1. ✅ **Use IAM users** instead of root account
2. ✅ **Use least privilege** - only grant what's needed
3. ✅ **Rotate access keys** regularly (every 90 days)
4. ✅ **Enable MFA** on IAM user if possible
5. ✅ **Don't share credentials** - each person should have their own user
6. ✅ **Delete unused access keys**

## Troubleshooting

### "Access Denied" errors:
- Check that policies are attached to the user
- Verify the access key is active
- Check region matches your resources

### "Cannot create IAM role":
- Ensure `iam:PassRole` permission is included
- Check that resource restrictions allow role creation

## Next Steps

After configuring AWS CLI, you can:

1. **Create EC2 Key Pair**:
   ```bash
   aws ec2 create-key-pair --key-name my-key --query 'KeyMaterial' --output text > my-key.pem
   chmod 400 my-key.pem
   ```

2. **Deploy your stack**:
   ```bash
   cd infrastructure
   ./deploy.sh
   ```

