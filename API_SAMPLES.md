# 🧪 Sample API Requests

## Ingest & Verify Workflow

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Ingest a Claim
```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "text": "COVID-19 vaccines contain microchips for tracking people",
    "source": "https://example.com/post/123",
    "source_type": "social",
    "metadata": {
      "platform": "twitter",
      "author": "user123"
    }
  }'
```

**Expected Response:**
```json
{
  "claim_id": "507f1f77bcf86cd799439011",
  "is_claim": true,
  "message": "Claim detected and stored successfully",
  "claim_detected": {
    "id": "507f1f77bcf86cd799439011",
    "claim_text": "COVID-19 vaccines contain microchips",
    "claim_type": "health",
    "confidence": 0.95,
    "entities": [
      {"text": "COVID-19", "type": "other"},
      {"text": "vaccines", "type": "other"},
      {"text": "microchips", "type": "other"}
    ]
  }
}
```

### 3. Verify the Claim
```bash
curl -X POST http://localhost:8000/api/verify/507f1f77bcf86cd799439011
```

**Expected Response:**
```json
{
  "id": "507f1f77bcf86cd799439012",
  "claim_id": "507f1f77bcf86cd799439011",
  "verdict": "False",
  "confidence": 0.98,
  "reasoning": "Multiple authoritative health organizations including WHO, CDC, and FDA have confirmed that COVID-19 vaccines do not contain microchips. The vaccines contain mRNA or viral vector components, along with standard pharmaceutical ingredients. The microchip claim has been debunked by fact-checkers worldwide.",
  "sources": [
    {
      "link": "https://www.who.int/emergencies/diseases/novel-coronavirus-2019/vaccine-tracker",
      "excerpt": "COVID-19 vaccines are safe and do not contain tracking devices",
      "title": "WHO COVID-19 Vaccine Tracker",
      "reliability": 0.98
    },
    {
      "link": "https://www.cdc.gov/coronavirus/2019-ncov/vaccines/facts.html",
      "excerpt": "Vaccines do not contain microchips. They contain ingredients that trigger immune response.",
      "title": "CDC Vaccine Facts",
      "reliability": 0.97
    }
  ],
  "explain_like_12": "Some people worry that COVID vaccines have tiny computers in them to track you, but that's not true. Scientists have checked what's in the vaccines, and it's just medicine stuff that helps your body fight the virus. There are no chips or tracking devices.",
  "harm_score": 75,
  "recommended_action": "debunk",
  "created_at": "2025-01-10T10:30:00Z"
}
```

### 4. Get All Claims
```bash
curl http://localhost:8000/api/claims?limit=10&claim_type=health
```

### 5. Get Claim Details
```bash
curl http://localhost:8000/api/claims/507f1f77bcf86cd799439011
```

### 6. Submit Feedback
```bash
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "claim_id": "507f1f77bcf86cd799439011",
    "feedback_type": "additional_evidence",
    "content": "Additional research from Johns Hopkins confirms this is false",
    "user_email": "researcher@example.com",
    "supporting_links": ["https://hopkins.edu/..."]
  }'
```

### 7. Get Trending Clusters
```bash
curl http://localhost:8000/api/clusters?limit=5
```

### 8. Refresh Clusters
```bash
curl -X POST http://localhost:8000/api/clusters/refresh?hours=24
```

### 9. Get Alerts
```bash
curl http://localhost:8000/api/alerts?severity=high&is_active=true
```

### 10. Get Statistics
```bash
curl http://localhost:8000/api/stats
```

---

## Test Claims

### Health Misinformation
```json
{
  "text": "Drinking bleach cures cancer",
  "source": "social_media",
  "source_type": "social"
}
```

### Political Misinformation
```json
{
  "text": "The 2020 election had millions of fraudulent votes",
  "source": "blog_post",
  "source_type": "blog"
}
```

### Science Misinformation
```json
{
  "text": "The Earth is flat and NASA is hiding the truth",
  "source": "forum_post",
  "source_type": "forum"
}
```

### True Claim
```json
{
  "text": "Water boils at 100 degrees Celsius at sea level",
  "source": "textbook",
  "source_type": "educational"
}
```

---

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Ingest claim
response = requests.post(f"{BASE_URL}/api/ingest", json={
    "text": "5G towers cause COVID-19",
    "source": "social_media",
    "source_type": "social"
})

claim_data = response.json()
claim_id = claim_data["claim_id"]

print(f"Claim ID: {claim_id}")

# Verify claim
verify_response = requests.post(f"{BASE_URL}/api/verify/{claim_id}")
verdict = verify_response.json()

print(f"Verdict: {verdict['verdict']}")
print(f"Confidence: {verdict['confidence']}")
print(f"Harm Score: {verdict['harm_score']}")
```

---

## JavaScript Client Example

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

async function checkClaim(text) {
  // Ingest
  const ingestRes = await axios.post(`${BASE_URL}/api/ingest`, {
    text: text,
    source: 'manual',
    source_type: 'manual'
  });
  
  const claimId = ingestRes.data.claim_id;
  console.log('Claim ID:', claimId);
  
  // Verify
  const verifyRes = await axios.post(`${BASE_URL}/api/verify/${claimId}`);
  const verdict = verifyRes.data;
  
  console.log('Verdict:', verdict.verdict);
  console.log('Confidence:', verdict.confidence);
  console.log('Explanation:', verdict.explain_like_12);
  
  return verdict;
}

checkClaim('Vaccines cause autism');
```
