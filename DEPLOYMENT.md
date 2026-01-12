# 🚀 Deployment Guide - coastalsevel SDLC Automation Platform

This guide provides comprehensive instructions for deploying the coastalsevel SDLC Automation Platform in various environments.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Node.js**: 16 or higher
- **Database**: PostgreSQL 12+ (SQLite for development)
- **Memory**: Minimum 4GB RAM (8GB+ recommended)
- **Storage**: 10GB+ available space

### Required Accounts & Services
- **GitHub Account**: For repository integration
- **Cloud Provider**: AWS, GCP, or Azure (for production)
- **Domain Name**: For production deployment (optional)

## 🏠 Local Development Setup

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd intigrationagent

# Run the startup script
python start_application.py
```

### Manual Setup
```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python reset_db.py
python setup_all_agents.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

### Environment Configuration
Create `backend/.env`:
```env
DATABASE_URL=sqlite:///./app.db
GROQ_API_KEY=your_groq_api_key_here
GITHUB_TOKEN=your_github_token_here
CORS_ORIGINS=["http://localhost:5173"]
SECRET_KEY=your-secret-key-change-in-production
```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Docker Build
```bash
# Build backend
cd backend
docker build -t coastalsevel-backend .

# Build frontend
cd ../frontend
docker build -t coastalsevel-frontend .

# Run containers
docker run -d -p 8000:8000 --name backend coastalsevel-backend
docker run -d -p 5173:5173 --name frontend coastalsevel-frontend
```

## ☁️ Cloud Deployment

### AWS Deployment

#### Option 1: AWS App Runner
```bash
# 1. Push code to GitHub
git push origin main

# 2. Create App Runner service for backend
aws apprunner create-service \
  --service-name coastalsevel-backend \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "your-account.dkr.ecr.region.amazonaws.com/coastalsevel-backend:latest",
      "ImageConfiguration": {
        "Port": "8000"
      }
    }
  }'

# 3. Create App Runner service for frontend
aws apprunner create-service \
  --service-name coastalsevel-frontend \
  --source-configuration '{
    "CodeRepository": {
      "RepositoryUrl": "https://github.com/your-username/coastalsevel-sdlc",
      "SourceCodeVersion": {
        "Type": "BRANCH",
        "Value": "main"
      }
    }
  }'
```

#### Option 2: AWS ECS with Fargate
```bash
# 1. Create ECS cluster
aws ecs create-cluster --cluster-name coastalsevel-cluster

# 2. Create task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# 3. Create service
aws ecs create-service \
  --cluster coastalsevel-cluster \
  --service-name coastalsevel-service \
  --task-definition coastalsevel-task \
  --desired-count 1 \
  --launch-type FARGATE
```

#### Option 3: AWS Lambda + API Gateway
```bash
# Install Serverless Framework
npm install -g serverless

# Deploy backend as Lambda
cd backend
serverless deploy

# Deploy frontend to S3 + CloudFront
cd ../frontend
npm run build
aws s3 sync dist/ s3://your-bucket-name --delete
```

### Google Cloud Platform (GCP)

#### Cloud Run Deployment
```bash
# 1. Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/coastalsevel-backend backend/
gcloud builds submit --tag gcr.io/PROJECT_ID/coastalsevel-frontend frontend/

# 2. Deploy to Cloud Run
gcloud run deploy coastalsevel-backend \
  --image gcr.io/PROJECT_ID/coastalsevel-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

gcloud run deploy coastalsevel-frontend \
  --image gcr.io/PROJECT_ID/coastalsevel-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### App Engine Deployment
```bash
# Backend (app.yaml)
cd backend
gcloud app deploy

# Frontend (separate service)
cd ../frontend
npm run build
gcloud app deploy --version frontend
```

### Microsoft Azure

#### Azure Container Instances
```bash
# Create resource group
az group create --name coastalsevel-rg --location eastus

# Deploy backend container
az container create \
  --resource-group coastalsevel-rg \
  --name coastalsevel-backend \
  --image your-registry/coastalsevel-backend:latest \
  --ports 8000 \
  --dns-name-label coastalsevel-backend

# Deploy frontend container
az container create \
  --resource-group coastalsevel-rg \
  --name coastalsevel-frontend \
  --image your-registry/coastalsevel-frontend:latest \
  --ports 80 \
  --dns-name-label coastalsevel-frontend
```

#### Azure App Service
```bash
# Create App Service plan
az appservice plan create \
  --name coastalsevel-plan \
  --resource-group coastalsevel-rg \
  --sku B1 \
  --is-linux

# Create web apps
az webapp create \
  --resource-group coastalsevel-rg \
  --plan coastalsevel-plan \
  --name coastalsevel-backend \
  --deployment-container-image-name your-registry/coastalsevel-backend:latest

az webapp create \
  --resource-group coastalsevel-rg \
  --plan coastalsevel-plan \
  --name coastalsevel-frontend \
  --deployment-container-image-name your-registry/coastalsevel-frontend:latest
```

## 🗄️ Database Setup

### PostgreSQL (Production)
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE coastalsevel_db;
CREATE USER coastalsevel_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE coastalsevel_db TO coastalsevel_user;
\q

# Update DATABASE_URL
DATABASE_URL=postgresql://coastalsevel_user:secure_password@localhost/coastalsevel_db
```

### Cloud Database Options

#### AWS RDS
```bash
aws rds create-db-instance \
  --db-instance-identifier coastalsevel-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password SecurePassword123 \
  --allocated-storage 20
```

#### Google Cloud SQL
```bash
gcloud sql instances create coastalsevel-db \
  --database-version POSTGRES_13 \
  --tier db-f1-micro \
  --region us-central1
```

#### Azure Database for PostgreSQL
```bash
az postgres server create \
  --resource-group coastalsevel-rg \
  --name coastalsevel-db \
  --location eastus \
  --admin-user admin \
  --admin-password SecurePassword123 \
  --sku-name B_Gen5_1
```

## 🔐 Security Configuration

### SSL/TLS Setup
```bash
# Using Let's Encrypt with Certbot
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### Environment Variables (Production)
```env
# Backend Production Environment
DATABASE_URL=postgresql://user:password@host:5432/dbname
GROQ_API_KEY=your_production_groq_key
GITHUB_TOKEN=your_production_github_token
CORS_ORIGINS=["https://yourdomain.com"]
SECRET_KEY=super-secure-secret-key-for-production
ENVIRONMENT=production
DEBUG=false
```

### Firewall Configuration
```bash
# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000  # Backend API
sudo ufw enable
```

## 📊 Monitoring & Logging

### Application Monitoring
```bash
# Install monitoring tools
pip install sentry-sdk prometheus-client

# Add to backend/app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
)
```

### Log Management
```bash
# Configure log rotation
sudo nano /etc/logrotate.d/coastalsevel

/var/log/coastalsevel/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
```

## 🔄 CI/CD Pipeline

### GitHub Actions
Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '16'
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Build and Deploy
        run: |
          # Build frontend
          cd frontend
          npm install
          npm run build
          
          # Deploy to your cloud provider
          # Add your deployment commands here
```

### Docker Registry Push
```bash
# Build and tag images
docker build -t your-registry/coastalsevel-backend:latest backend/
docker build -t your-registry/coastalsevel-frontend:latest frontend/

# Push to registry
docker push your-registry/coastalsevel-backend:latest
docker push your-registry/coastalsevel-frontend:latest
```

## 🧪 Testing Deployment

### Health Checks
```bash
# Backend health check
curl http://your-domain:8000/api/test

# Frontend check
curl http://your-domain:5173

# Full workflow test
curl -X POST http://your-domain:8000/api/agents/orchestrate-sdlc \
  -F "query=Test project" \
  -F "file=@test-prd.pdf"
```

### Load Testing
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test backend performance
ab -n 1000 -c 10 http://your-domain:8000/api/test

# Test with wrk
wrk -t12 -c400 -d30s http://your-domain:8000/api/test
```

## 🚨 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check logs
docker logs coastalsevel-backend

# Check database connection
python -c "from app.core.database import engine; print(engine.execute('SELECT 1').scalar())"

# Check environment variables
env | grep -E "(DATABASE_URL|GROQ_API_KEY|GITHUB_TOKEN)"
```

#### Frontend Build Fails
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version
npm --version

# Build with verbose output
npm run build --verbose
```

#### Database Connection Issues
```bash
# Test database connection
psql $DATABASE_URL -c "SELECT version();"

# Check database permissions
psql $DATABASE_URL -c "\du"

# Reset database
python reset_db.py
```

### Performance Optimization

#### Backend Optimization
```python
# Add to main.py
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Enable caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

FastAPICache.init(RedisBackend(), prefix="fastapi-cache")
```

#### Frontend Optimization
```bash
# Build with optimization
npm run build

# Analyze bundle size
npm install -g webpack-bundle-analyzer
npx webpack-bundle-analyzer dist/static/js/*.js
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Use load balancers (AWS ALB, GCP Load Balancer, Azure Load Balancer)
- Implement session management with Redis
- Use CDN for static assets
- Database read replicas for read-heavy workloads

### Vertical Scaling
- Monitor CPU and memory usage
- Increase container resources as needed
- Optimize database queries
- Implement caching strategies

## 🔒 Security Checklist

- [ ] HTTPS enabled with valid SSL certificate
- [ ] Environment variables secured
- [ ] Database credentials rotated regularly
- [ ] API rate limiting implemented
- [ ] Input validation and sanitization
- [ ] CORS properly configured
- [ ] Security headers implemented
- [ ] Regular security updates applied
- [ ] Monitoring and alerting configured
- [ ] Backup and disaster recovery plan

## 📞 Support

For deployment issues:
1. Check the troubleshooting section above
2. Review application logs
3. Verify environment configuration
4. Test individual components
5. Create an issue in the GitHub repository

---

**🎉 Congratulations!** Your coastalsevel SDLC Automation Platform is now deployed and ready to automate software development workflows!