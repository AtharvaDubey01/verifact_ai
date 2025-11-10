# 🛡️ CrisisGuard AI - Real-Time Misinformation Detection Platform

**A production-ready AI-powered fact-verification system** built for hackathons and real-world deployment.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![React](https://img.shields.io/badge/react-18.2-blue.svg)

---

## 📋 Overview

CrisisGuard AI (aka VeriFacts) is a complete misinformation detection and verification platform that:

- ✅ **Detects claims** in text using AI
- ✅ **Retrieves evidence** from multiple authoritative sources
- ✅ **Fact-checks claims** with LLM reasoning agents
- ✅ **Clusters similar claims** to identify viral misinformation
- ✅ **Provides human review** workflow
- ✅ **Sends alerts** for high-harm content
- ✅ **Delivers clear explanations** (expert + "explain like I'm 12")

---

## 🎯 Key Features

### AI-Powered Fact-Checking
- **Claim Detection Agent**: Identifies verifiable claims in text
- **Evidence Retrieval Agent**: Searches Google Fact Check API, NewsAPI, and more
- **Fact-Checker Agent**: GPT-4o/Claude powered reasoning with safety guardrails
- **Summarizer Agent**: Generates expert + child-friendly explanations

### Real-Time Analytics
- **FAISS Vector Search**: Similarity-based claim clustering
- **HDBSCAN Clustering**: Identifies trending misinformation topics
- **Harm Scoring**: 0-100 scale for content danger assessment

### Production-Ready Architecture
- **FastAPI Backend**: Async API with 8 endpoints
- **MongoDB**: Scalable NoSQL storage
- **Redis**: Caching and job queuing
- **React + Vite Frontend**: Modern, responsive UI
- **Docker Compose**: One-command deployment

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API key (required)
- NewsAPI key (optional but recommended)
- Google Fact Check API key (optional)

### 1. Clone & Configure

```bash
cd "untitled folder"
```

Copy environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
OPENAI_API_KEY=sk-your-key-here
NEWS_API_KEY=your-newsapi-key
GOOGLE_FACTCHECK_API_KEY=your-google-key
```

### 2. Launch with Docker

```bash
docker-compose up --build
```

This starts:
- **Backend API**: http://localhost:8000
- **Frontend UI**: http://localhost:5173
- **MongoDB**: localhost:27017
- **Redis**: localhost:6379

### 3. Access the Platform

Open your browser to:
- **Dashboard**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📊 Architecture

```
CrisisGuard AI
│
├── Backend (Python + FastAPI)
│   ├── AI Agents
│   │   ├── Claim Detector (GPT-4o)
│   │   ├── Evidence Retriever (Multi-source)
│   │   ├── Fact-Checker (LLM reasoning)
│   │   └── Summarizer (Explanations)
│   │
│   ├── Services
│   │   ├── Embedding Service (OpenAI + FAISS)
│   │   └── Clustering Service (HDBSCAN)
│   │
│   ├── Database
│   │   ├── MongoDB (Claims, Verdicts, Evidence)
│   │   └── Redis (Cache, Queue)
│   │
│   └── API Routes
│       ├── /api/ingest - Ingest text
│       ├── /api/verify/{id} - Fact-check claim
│       ├── /api/claims - List claims
│       ├── /api/clusters - Trending topics
│       └── /api/alerts - High-harm alerts
│
└── Frontend (React + Vite + Tailwind)
    ├── Pages
    │   ├── Dashboard (Stats + Overview)
    │   ├── Claims List (Browse & Filter)
    │   ├── Claim Detail (Full analysis)
    │   ├── Trending Clusters
    │   ├── Human Review Queue
    │   └── Alerts Panel
    │
    └── Components
        ├── ClaimCard
        ├── VerdictPill
        ├── EvidenceCard
        └── Layout (Sidebar + TopNav)
```

---

## 🔧 API Endpoints

### Core Endpoints

#### 1. Ingest Text
```bash
POST /api/ingest
Content-Type: application/json

{
  "text": "The moon landing was faked in 1969",
  "source": "https://example.com/post/123",
  "source_type": "social"
}
```

**Response:**
```json
{
  "claim_id": "507f1f77bcf86cd799439011",
  "is_claim": true,
  "message": "Claim detected and stored successfully",
  "claim_detected": {
    "id": "507f1f77bcf86cd799439011",
    "claim_text": "The moon landing was faked in 1969",
    "claim_type": "science",
    "confidence": 0.92
  }
}
```

#### 2. Verify Claim
```bash
POST /api/verify/507f1f77bcf86cd799439011
```

**Response:**
```json
{
  "verdict": "False",
  "confidence": 0.95,
  "reasoning": "Multiple authoritative sources confirm...",
  "sources": [
    {
      "link": "https://nasa.gov/...",
      "excerpt": "...",
      "reliability": 0.98
    }
  ],
  "explain_like_12": "People really did land on the moon...",
  "harm_score": 35,
  "recommended_action": "debunk"
}
```

#### 3. Get Claims
```bash
GET /api/claims?claim_type=health&status=verified&limit=20
```

#### 4. Get Trending Clusters
```bash
GET /api/clusters?limit=10
```

#### 5. Submit Feedback
```bash
POST /api/feedback
{
  "claim_id": "507f1f77bcf86cd799439011",
  "feedback_type": "correction",
  "content": "Additional evidence suggests..."
}
```

---

## 🧪 Sample Workflow

### End-to-End Example

1. **Ingest a claim**:
```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Drinking bleach cures COVID-19",
    "source": "social_media_post",
    "source_type": "social"
  }'
```

2. **Verify the claim** (returns claim_id from step 1):
```bash
curl -X POST http://localhost:8000/api/verify/{claim_id}
```

3. **View in UI**:
   - Go to http://localhost:5173/claims
   - Click on the claim to see full analysis
   - Review verdict, evidence sources, and harm score

---

## 🎨 Frontend Features

### Dashboard
- **Real-time stats**: Total claims, verified count, trending clusters
- **Verdict breakdown chart**: Visual distribution of True/False/Misleading
- **Recent claims feed**
- **One-click ingestion modal**

### Claim Detail Page
- **Full verdict analysis** with confidence score
- **Harm potential meter** (0-100 scale)
- **Expert reasoning** + "Explain like I'm 12"
- **Evidence sources** with reliability ratings
- **Similar claims** (vector similarity)
- **Community feedback** form

### Trending Clusters
- **Clustered claims** showing viral patterns
- **Trend score** visualization
- **Representative claim** for each cluster

### Human Review Queue
- **Approve/reject** AI verdicts
- **Override verdicts** with manual review
- **Add reviewer notes**

### Alerts Panel
- **High-harm claim alerts** (score ≥ 70)
- **Severity filtering** (Critical/High/Medium/Low)
- **Resolve alerts** workflow

---

## 🔐 Safety & Ethics

### Built-in Guardrails

1. **No Hallucinated Citations**
   - LLM can only cite sources from provided evidence
   - Validation ensures URLs match retrieved evidence

2. **Harm Scoring**
   - 0-20: Harmless
   - 21-40: Minor misinformation
   - 41-60: Moderate potential harm
   - 61-80: Significant harm (health, safety, democracy)
   - 81-100: Crisis-level (violence incitement, public health emergency)

3. **Transparency**
   - All reasoning is logged
   - Human review required for publication
   - Confidence scores displayed

4. **Evidence Quality**
   - Reliability scoring for all sources
   - Preference for gov/academic/fact-check sites
   - Cross-referencing multiple sources

---

## 📁 Project Structure

```
untitled folder/
├── backend/
│   ├── agents/
│   │   ├── claim_detector.py
│   │   ├── evidence_retriever.py
│   │   ├── fact_checker.py
│   │   └── prompts.py
│   ├── database/
│   │   └── connection.py
│   ├── models/
│   │   └── schemas.py
│   ├── routers/
│   │   ├── claims.py
│   │   ├── verification.py
│   │   ├── clusters.py
│   │   ├── feedback.py
│   │   └── alerts.py
│   ├── services/
│   │   ├── embedding_service.py
│   │   └── clustering_service.py
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js
│   │   ├── components/
│   │   │   ├── Layout.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── TopNav.jsx
│   │   │   ├── ClaimCard.jsx
│   │   │   ├── VerdictPill.jsx
│   │   │   └── EvidenceCard.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── ClaimsList.jsx
│   │   │   ├── ClaimDetail.jsx
│   │   │   ├── TrendingClusters.jsx
│   │   │   ├── HumanReview.jsx
│   │   │   └── Alerts.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🛠️ Tech Stack

### Backend
- **Python 3.11** - Modern async Python
- **FastAPI** - High-performance web framework
- **MongoDB** - Flexible document database
- **Redis** - Caching & job queue
- **FAISS** - Vector similarity search
- **OpenAI GPT-4o** - LLM reasoning
- **HDBSCAN** - Clustering algorithm

### Frontend
- **React 18** - UI framework
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first styling
- **Recharts** - Data visualization
- **React Router** - Navigation
- **Axios** - HTTP client

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-service orchestration
- **Uvicorn** - ASGI server

---

## 📈 Performance

- **Claim Detection**: ~2-3 seconds
- **Full Verification**: ~10-15 seconds (depends on evidence retrieval)
- **Clustering**: Batch process (every 1-24 hours)
- **API Response Time**: <500ms for most endpoints

---

## 🧩 Extensibility

### Adding New Evidence Sources

Edit `backend/agents/evidence_retriever.py`:

```python
async def _search_custom_source(self, query: str):
    # Add your custom API integration
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com?q={query}")
        # Parse and return sources
```

### Custom Claim Types

Edit `backend/models/schemas.py`:

```python
claim_type: str = Field(
    default="general", 
    regex="^(health|politics|general|science|business|YOUR_TYPE)$"
)
```

### Alternative LLMs

Edit `backend/agents/fact_checker.py` to use Claude, Llama, etc.:

```python
from anthropic import AsyncAnthropic

self.client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Rebuild
docker-compose down
docker-compose up --build
```

### MongoDB connection failed
```bash
# Verify MongoDB is running
docker-compose ps

# Reset volumes
docker-compose down -v
docker-compose up
```

### Frontend not loading
```bash
# Check if backend is accessible
curl http://localhost:8000/health

# Rebuild frontend
cd frontend
npm install
npm run dev
```

---

## 📝 License

MIT License - See LICENSE file for details

---

## 👥 Contributing

This is a hackathon project built for demonstration. For production use:

1. Add authentication & authorization
2. Implement rate limiting
3. Add comprehensive error handling
4. Set up monitoring (Sentry, DataDog, etc.)
5. Add unit & integration tests
6. Configure CI/CD pipelines
7. Use production-grade LLM API keys

---

## 🎉 Acknowledgments

- **OpenAI** - GPT-4o API
- **NewsAPI** - News article search
- **Google** - Fact Check Tools API
- **FAISS** - Vector similarity search
- **React** - UI framework
- **FastAPI** - Web framework

---

## 📞 Support

For questions or issues:
- Create a GitHub issue
- Review API documentation at http://localhost:8000/docs
- Check Docker logs: `docker-compose logs -f`

---

**Built with ❤️ for fighting misinformation**

*"The best way to fight misinformation is with better information."*
