# AMS Deployment Guide

This guide covers deploying the Article Market Simulator (AMS) application.

## Prerequisites

- Docker and Docker Compose installed
- API keys for LLM providers (Gemini/OpenAI)
- Domain name (for production deployment)
- SSL certificates (for HTTPS)

## Configuration

### 1. Environment Variables

Create a `.env` file in the root directory:

```bash
# LLM Provider Keys
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key

# Application Settings
ENV=production
LOG_LEVEL=INFO
```

### 2. Frontend Configuration

Update the API URL in `frontend/.env`:

```bash
VITE_API_URL=https://your-domain.com/api
```

## Deployment Options

### Option 1: Docker Compose (Recommended)

#### Development Deployment

```bash
# Build and start all services
docker-compose up --build

# Services will be available at:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

#### Production Deployment

```bash
# Build and start with production profile
docker-compose --profile production up --build -d

# Services will be available at:
# - Main site: http://your-domain.com (via nginx)
# - Direct access: 
#   - Frontend: http://your-domain.com:3000
#   - Backend: http://your-domain.com:8000
```

### Option 2: Manual Deployment

#### Backend Deployment

1. Install dependencies:
```bash
poetry install --only main
```

2. Run with production server:
```bash
gunicorn src.server.app:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

#### Frontend Deployment

1. Build the frontend:
```bash
cd frontend
npm install
npm run build
```

2. Serve with nginx or any static file server:
```bash
# Copy dist files to web server
cp -r dist/* /var/www/ams/
```

### Option 3: Cloud Deployment

#### AWS ECS/Fargate

1. Build and push Docker images to ECR:
```bash
# Backend
docker build -t ams-backend .
docker tag ams-backend:latest <ecr-uri>/ams-backend:latest
docker push <ecr-uri>/ams-backend:latest

# Frontend
cd frontend
docker build -t ams-frontend .
docker tag ams-frontend:latest <ecr-uri>/ams-frontend:latest
docker push <ecr-uri>/ams-frontend:latest
```

2. Create ECS task definitions and services

#### Google Cloud Run

```bash
# Backend
gcloud run deploy ams-backend \
  --image gcr.io/your-project/ams-backend \
  --platform managed \
  --allow-unauthenticated

# Frontend (using Cloud CDN)
gsutil -m cp -r frontend/dist/* gs://your-bucket/
```

## Monitoring & Maintenance

### Health Checks

Both services expose health endpoints:
- Backend: `GET /health`
- Frontend: `GET /health`

### Logs

- Backend logs: Available in Docker logs or `/app/logs/`
- Frontend logs: Nginx access/error logs

### Scaling

For horizontal scaling:
1. Backend: Increase worker count or container replicas
2. Frontend: Use CDN for static assets
3. Consider adding Redis for session/cache management

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **HTTPS**: Always use HTTPS in production
3. **CORS**: Configure appropriate CORS origins
4. **Rate Limiting**: Implement rate limiting for API endpoints
5. **Authentication**: Add authentication for production use

## Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   - Check CORS configuration
   - Ensure WebSocket upgrade headers are proxied

2. **API Connection Errors**
   - Verify VITE_API_URL is correct
   - Check network connectivity between services

3. **High Memory Usage**
   - Adjust worker count
   - Implement request queuing for heavy simulations

### Debug Mode

Run with debug logging:
```bash
LOG_LEVEL=DEBUG docker-compose up
```

## Backup & Recovery

### Database Backup (if using persistent storage)
```bash
docker exec ams-backend python -m scripts.backup
```

### Restore
```bash
docker exec ams-backend python -m scripts.restore backup.tar.gz
```

## Performance Optimization

1. **Enable Caching**
   - Add Redis for caching simulation results
   - Use CDN for frontend assets

2. **Optimize LLM Calls**
   - Batch persona evaluations
   - Cache common patterns

3. **Frontend Optimization**
   - Enable gzip compression
   - Lazy load heavy components
   - Optimize bundle size

## Updating

1. Pull latest changes:
```bash
git pull origin main
```

2. Rebuild and restart:
```bash
docker-compose down
docker-compose up --build -d
```

3. Run migrations (if any):
```bash
docker exec ams-backend python -m scripts.migrate
```