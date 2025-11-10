# 🚀 Deployment Guide

## Local Development

### Prerequisites
- Docker Desktop installed
- 8GB RAM minimum
- OpenAI API key

### Steps

1. **Environment Setup**
```bash
cp .env.example .env
# Edit .env with your API keys
```

2. **Start Services**
```bash
docker-compose up --build
```

3. **Access Application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Production Deployment

### Option 1: Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml crisisguard

# Scale services
docker service scale crisisguard_backend=3
```

### Option 2: Kubernetes

Create `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crisisguard-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: crisisguard-backend
  template:
    metadata:
      labels:
        app: crisisguard-backend
    spec:
      containers:
      - name: backend
        image: crisisguard-backend:latest
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai
```

Deploy:
```bash
kubectl apply -f k8s-deployment.yaml
```

### Option 3: Cloud Platforms

#### AWS (ECS + RDS)
- Deploy containers to ECS Fargate
- Use RDS for MongoDB (DocumentDB)
- Use ElastiCache for Redis
- CloudFront for frontend

#### Google Cloud (Cloud Run)
- Deploy backend to Cloud Run
- Use Cloud Firestore
- Use Memorystore for Redis

#### Azure (Container Apps)
- Deploy to Azure Container Apps
- Use Cosmos DB
- Use Azure Cache for Redis

---

## Environment Variables

### Required
```env
OPENAI_API_KEY=sk-xxx
MONGODB_URI=mongodb://localhost:27017/crisisguard
REDIS_URL=redis://localhost:6379/0
```

### Optional
```env
NEWS_API_KEY=xxx
GOOGLE_FACTCHECK_API_KEY=xxx
LLM_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-large
```

---

## Monitoring

### Add Logging
Install in backend:
```bash
pip install sentry-sdk
```

Configure in `main.py`:
```python
import sentry_sdk
sentry_sdk.init(dsn="YOUR_SENTRY_DSN")
```

### Health Checks
```bash
curl http://localhost:8000/health
```

---

## Scaling

### Backend Scaling
```bash
docker-compose up --scale backend=3
```

### Database Indexing
Already configured in `init-mongo.js`

### Caching Strategy
- Redis for API responses
- 5-minute TTL for stats
- 1-hour TTL for verdicts

---

## Security Checklist

- [ ] Change SECRET_KEY in .env
- [ ] Enable HTTPS
- [ ] Add rate limiting
- [ ] Implement authentication
- [ ] Use API key rotation
- [ ] Enable CORS only for known origins
- [ ] Add input validation
- [ ] Set up firewall rules
- [ ] Enable logging & monitoring
- [ ] Regular dependency updates
