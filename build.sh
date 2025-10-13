#!/bin/bash
# Build script for Render deployment
# This script installs Tesseract OCR and other system dependencies

echo "🚀 Starting Render build process..."

# Update package lists
echo "📦 Updating package lists..."
apt-get update

# Install Tesseract OCR and dependencies
echo "🔤 Installing Tesseract OCR..."
apt-get install -y tesseract-ocr tesseract-ocr-eng

# Install additional system dependencies
echo "📚 Installing system dependencies..."
apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgcc-s1

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Build completed successfully!"
