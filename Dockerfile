# Stage 1: Build the React + Vite frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production Python runtime
FROM python:3.11-slim AS production
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    DATABASE_URL=sqlite:////app/instance/anika.db

# Install system dependencies (curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and source files
COPY . .

# Copy built frontend assets from Stage 1 into /app/dist
COPY --from=frontend-builder /app/dist /app/dist

# Ensure directories exist and train ML model
RUN mkdir -p /app/instance /app/uploads && \
    python backend/ml/train_category_model.py

EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT}/api/health || exit 1

# Start Gunicorn WSGI server
CMD gunicorn "backend.app:create_app()" --bind 0.0.0.0:${PORT} --workers 2 --timeout 120

