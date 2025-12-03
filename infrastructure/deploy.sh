#!/bin/bash
# Deployment script for AI Image Organizer on AWS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}AI Image Organizer - AWS Deployment${NC}"
echo "=========================================="

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    echo "Install it from: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi

# Get deployment method
echo ""
echo "Select deployment method:"
echo "1) EC2 (CloudFormation)"
echo "2) App Runner (Serverless)"
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        echo -e "${YELLOW}Deploying to EC2...${NC}"
        
        # Get parameters
        read -p "Enter Key Pair Name: " keypair
        read -p "Enter Instance Type [t2.micro/t3.micro]: " instancetype
        instancetype=${instancetype:-t2.micro}
        
        # Get region
        region=$(aws configure get region)
        region=${region:-us-east-1}
        
        # Update AMI ID for the region (Amazon Linux 2023)
        # You may need to update this for your region
        echo -e "${YELLOW}Note: Update AMI ID in cloudformation-template.yaml for region: $region${NC}"
        
        # Deploy CloudFormation stack
        stack_name="ai-image-organizer-$(date +%s)"
        aws cloudformation create-stack \
            --stack-name "$stack_name" \
            --template-body file://infrastructure/cloudformation-template.yaml \
            --parameters \
                ParameterKey=InstanceType,ParameterValue=$instancetype \
                ParameterKey=KeyPairName,ParameterValue=$keypair \
            --capabilities CAPABILITY_NAMED_IAM \
            --region $region
        
        echo -e "${GREEN}Stack creation started: $stack_name${NC}"
        echo "Monitor progress: aws cloudformation describe-stacks --stack-name $stack_name"
        ;;
    
    2)
        echo -e "${YELLOW}Deploying to App Runner...${NC}"
        
        read -p "Enter GitHub Connection ARN: " connection_arn
        read -p "Enter Repository URL: " repo_url
        read -p "Enter Branch [main]: " branch
        branch=${branch:-main}
        
        # Deploy App Runner
        aws apprunner create-service \
            --service-name ai-image-organizer \
            --source-configuration "{
                \"AuthenticationConfiguration\": {
                    \"ConnectionArn\": \"$connection_arn\"
                },
                \"CodeRepository\": {
                    \"RepositoryUrl\": \"$repo_url\",
                    \"SourceCodeVersion\": {
                        \"Type\": \"BRANCH\",
                        \"Value\": \"$branch\"
                    },
                    \"CodeConfiguration\": {
                        \"ConfigurationSource\": \"API\",
                        \"CodeConfigurationValues\": {
                            \"Runtime\": \"PYTHON_3\",
                            \"BuildCommand\": \"pip install -r requirements.txt\",
                            \"StartCommand\": \"uvicorn backend.app.main:app --host 0.0.0.0 --port 8000\"
                        }
                    }
                }
            }" \
            --instance-configuration "{
                \"Cpu\": \"0.25 vCPU\",
                \"Memory\": \"0.5 GB\"
            }"
        
        echo -e "${GREEN}App Runner service creation started${NC}"
        ;;
    
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Deployment initiated!${NC}"
echo "Remember to:"
echo "1. Set environment variables (Cloudinary, etc.)"
echo "2. Configure database if using RDS"
echo "3. Update security groups if needed"

