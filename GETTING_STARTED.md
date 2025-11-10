# 🚀 GETTING STARTED - CrisisGuard AI

**Complete walkthrough from zero to running platform in 10 minutes**

---

## ⏱️ Time to Launch: ~10 Minutes

### Prerequisites Check (2 minutes)

**Required:**
- [ ] Docker Desktop installed
- [ ] OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- [ ] 8GB RAM available
- [ ] 10GB disk space

**Optional (Recommended):**
- [ ] NewsAPI key ([Get here](https://newsapi.org/register))
- [ ] Google Fact Check API key ([Get here](https://console.cloud.google.com/))

---

## 🎯 Quick Start (3 Methods)

### Method 1: Automatic (Recommended) ⚡

```bash
cd "untitled folder"
./start.sh
```

**That's it!** The script will:
1. Check for .env file
2. Prompt you to add API keys if needed
3. Build and start all services
4. Run health checks
5. Display access URLs

---

### Method 2: Manual (Step-by-Step) 📋

#### Step 1: Configure Environment (1 minute)
```bash
cd "untitled folder"
cp .env.example .env
```

Edit `.env` and add your keys:
```bash
# Open .env in any text editor
nano .env
# OR
code .env
# OR
open -a TextEdit .env
```

**Minimum Required:**
```env
OPENAI_API_KEY=sk-your-openai-key-here
```

**Recommended (for full functionality):**
```env
OPENAI_API_KEY=sk-your-openai-key-here
NEWS_API_KEY=your-newsapi-key-here
GOOGLE_FACTCHECK_API_KEY=your-google-key-here
```

#### Step 2: Launch Services (5 minutes)
```bash
docker-compose up --build
```

Wait for:
```
✅ backend_1  | Application startup complete
✅ frontend_1 | ready in X ms
✅ mongodb_1  | Waiting for connections
✅ redis_1    | Ready to accept connections
```

#### Step 3: Access Platform
Open in browser:
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

---

### Method 3: Docker Commands (Advanced) 🐳

```bash
# Build images
docker-compose build

# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Stop everything
docker-compose down
```

---

## 🎮 First Use Tutorial

### 1. Verify Installation

Open http://localhost:5173

You should see:
- ✅ Dashboard with stats
- ✅ Sidebar navigation
- ✅ Search bar
- ✅ "Ingest New Claim" button

### 2. Test the API (Terminal)

```bash
# Health check
curl http://localhost:8000/health

# Expected: {"status": "healthy", ...}
```

### 3. Ingest Your First Claim

**Option A: Via UI**
1. Click "Ingest New Claim" button
2. Paste: `"COVID-19 vaccines contain microchips"`
3. Click "Analyze Text"
4. Wait 2-3 seconds
5. See result!

**Option B: Via API**
```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "text": "COVID-19 vaccines contain microchips",
    "source": "test",
    "source_type": "manual"
  }'
```

### 4. Verify the Claim

1. Copy the `claim_id` from response
2. Click "Verify Claim" in UI, or:

```bash
curl -X POST http://localhost:8000/api/verify/YOUR_CLAIM_ID
```

Wait 10-15 seconds for:
- ✅ Evidence retrieval
- ✅ Fact-checking
- ✅ Verdict generation

### 5. View Results

Navigate to: http://localhost:5173/claims/YOUR_CLAIM_ID

You'll see:
- ✅ Verdict (True/False/Misleading/etc.)
- ✅ Confidence score
- ✅ Expert reasoning
- ✅ "Explain like I'm 12" version
- ✅ Evidence sources
- ✅ Harm score
- ✅ Similar claims

---

## 🧪 Test Claims to Try

### Health Misinformation
```
"Drinking bleach cures COVID-19"
```
Expected: `False`, High Harm Score

### Science Facts
```
"Water boils at 100 degrees Celsius at sea level"
```
Expected: `True`, Low Harm Score

### Political Claims
```
"The 2020 US election had millions of fraudulent votes"
```
Expected: `False`, High Harm Score

### Ambiguous Claims
```
"Climate change will end civilization"
```
Expected: `Misleading` or `Partially True`

---

## 📚 Next Steps

### Explore Features

1. **Dashboard** (/)
   - View overall statistics
   - See recent claims
   - Check trending topics
   - Monitor verdict breakdown

2. **Claims List** (/claims)
   - Browse all claims
   - Filter by type/status
   - Search functionality

3. **Trending** (/trending)
   - See clustered claims
   - Identify viral patterns
   - Monitor trend scores

4. **Review Queue** (/review)
   - Human oversight
   - Approve/reject verdicts
   - Add reviewer notes

5. **Alerts** (/alerts)
   - High-harm notifications
   - Filter by severity
   - Resolve alerts

### Test API Endpoints

Visit: http://localhost:8000/docs

Try:
- `POST /api/ingest` - Submit new text
- `POST /api/verify/{id}` - Fact-check claim
- `GET /api/claims` - List all claims
- `GET /api/clusters` - Trending topics
- `POST /api/feedback` - Submit feedback

### Check Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend

# Database
docker-compose logs -f mongodb
```

---

## 🔧 Troubleshooting

### Issue: "Cannot connect to Docker"
**Solution:**
```bash
# Start Docker Desktop first
# Wait for Docker icon in menu bar/tray
# Then retry: docker-compose up
```

### Issue: "Port already in use"
**Solution:**
```bash
# Check what's using port 8000
lsof -i :8000

# Kill process or change port in docker-compose.yml
```

### Issue: "Backend returns 500 error"
**Solution:**
```bash
# Check backend logs
docker-compose logs backend

# Verify API key is set
docker-compose exec backend env | grep OPENAI

# Restart backend
docker-compose restart backend
```

### Issue: "Frontend shows blank page"
**Solution:**
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up --build frontend

# Clear browser cache
```

### Issue: "Claim detection fails"
**Solution:**
```bash
# Verify OpenAI API key is valid
# Check you have API credits
# View error in logs: docker-compose logs backend
```

---

## 🛑 Stopping the Platform

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (reset database)
docker-compose down -v

# Stop but keep containers
docker-compose stop
```

---

## 🔄 Restarting

```bash
# Quick restart
docker-compose restart

# Full rebuild
docker-compose down
docker-compose up --build

# Just backend
docker-compose restart backend
```

---

## 📊 Monitoring

### Check Service Status
```bash
docker-compose ps
```

### View Resource Usage
```bash
docker stats
```

### Database Access
```bash
# MongoDB shell
docker-compose exec mongodb mongosh crisisguard

# Redis CLI
docker-compose exec redis redis-cli
```

---

## 🎓 Learning Resources

### Architecture
- Read: `README.md` - Complete overview
- Read: `FILE_STRUCTURE.md` - Code organization
- Read: `PROJECT_SUMMARY.md` - Feature details

### API Usage
- Read: `API_SAMPLES.md` - Example requests
- Visit: http://localhost:8000/docs - Interactive API docs

### Deployment
- Read: `DEPLOYMENT.md` - Production deployment

---

## ✅ Success Indicators

You know it's working when:

✅ Frontend loads at http://localhost:5173  
✅ Dashboard shows stats  
✅ Can ingest test claim  
✅ Verification returns verdict  
✅ Evidence sources displayed  
✅ No errors in logs  
✅ Health endpoint returns "healthy"  

---

## 💡 Pro Tips

1. **Keep Docker Desktop Running** - Required for all operations
2. **Use Chrome DevTools** - Network tab shows API calls
3. **Monitor Logs** - `docker-compose logs -f` shows real-time activity
4. **Test with Real Claims** - More interesting than fake examples
5. **Try Different Claim Types** - Health, politics, science behave differently
6. **Check Harm Scores** - High scores trigger alerts
7. **Explore Clustering** - Run `/api/clusters/refresh` to see grouping

---

## 🚀 You're Ready!

Your CrisisGuard AI platform is now running. Start fighting misinformation! 🛡️

**Questions?**
- Check logs: `docker-compose logs -f`
- Review docs: `README.md`
- Test API: http://localhost:8000/docs
- View health: http://localhost:8000/health

---

**Happy Fact-Checking! 🎉**
