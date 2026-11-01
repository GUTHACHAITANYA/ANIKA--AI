#!/usr/bin/env bash
# Exit immediately if any command fails
set -o errexit

echo ">>> [1/5] Installing Node dependencies..."
npm install

echo ">>> [2/5] Building React Vite production bundle..."
npm run build

echo ">>> [3/5] Installing Python backend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ">>> [4/5] Verifying & generating ML category model..."
python backend/ml/train_category_model.py

echo ">>> [5/5] Initializing runtime directories & database schema..."
mkdir -p instance uploads
python -c "from backend.app import create_app; create_app()"

echo ">>> Deployment build successfully completed!"
