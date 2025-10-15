#!/bin/bash
# Azure Deployment Script for Elemental Circle Game

echo "🚀 Deploying Elemental Circle Game to Azure..."

# Set variables
APP_NAME="elemental-circle"
RESOURCE_GROUP="elemental-rg"
LOCATION="eastus"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Please install Azure CLI first."
    exit 1
fi

echo "🔐 Logging into Azure..."
az login

echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

echo "🐳 Creating Azure Container Registry..."
az acr create --resource-group $RESOURCE_GROUP --name $APP_NAME --sku Basic

echo "🏷️ Building and pushing image..."
az acr build --registry $APP_NAME --image $APP_NAME:latest .

echo "☸️ Creating AKS cluster..."
az aks create --resource-group $RESOURCE_GROUP --name $APP_NAME-cluster --node-count 2 --enable-addons monitoring --generate-ssh-keys

echo "🔑 Getting AKS credentials..."
az aks get-credentials --resource-group $RESOURCE_GROUP --name $APP_NAME-cluster

echo "📤 Deploying to AKS..."
kubectl apply -f k8s/

echo "✅ Deployment complete!"
echo "🌐 Your game will be available at: https://your-domain.com"





