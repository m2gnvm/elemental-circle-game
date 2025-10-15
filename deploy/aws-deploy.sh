#!/bin/bash
# AWS Deployment Script for Elemental Circle Game

echo "🚀 Deploying Elemental Circle Game to AWS..."

# Set variables
APP_NAME="elemental-circle"
REGION="us-east-1"
CLUSTER_NAME="elemental-cluster"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install AWS CLI first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker not running. Please start Docker first."
    exit 1
fi

echo "📦 Building Docker image..."
docker build -t $APP_NAME:latest .

echo "🏷️ Tagging image for ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com

ECR_REPO=$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com/$APP_NAME
docker tag $APP_NAME:latest $ECR_REPO:latest

echo "📤 Pushing to ECR..."
docker push $ECR_REPO:latest

echo "☸️ Deploying to EKS..."
kubectl apply -f k8s/

echo "✅ Deployment complete!"
echo "🌐 Your game will be available at: https://your-domain.com"





