#!/usr/bin/env bash
# Exit immediately if any command fails
set -o errexit

echo ">>> [1/4] Installing Node dependencies..."
npm install

echo ">>> [2/4] Building React Vite production bundle..."
npm run build

echo ">>> [3/4] Installing Python backend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ">>> [4/4] Verifying & generating ML category model..."
python backend/ml/train_category_model.py

echo ">>> Deployment build successfully completed!"
