"""
MongoDB Schemas for CrisisGuard AI
Complete database models with Pydantic validation
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, validator
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


# ============ CLAIM MODELS ============

class ClaimEntity(BaseModel):
    """Extracted entity from claim"""
    text: str
    type: str  # person, organization, location, date, etc.
    confidence: float = Field(ge=0.0, le=1.0)


class ClaimBase(BaseModel):
    """Base claim model"""
    claim_text: str = Field(..., min_length=10, max_length=5000)
    source: str  # URL or platform identifier
    source_type: str = "manual"  # manual, twitter, facebook, news, rss
    entities: List[ClaimEntity] = []
    claim_type: str = Field(default="general", regex="^(health|politics|general|science|business)$")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    language: str = "en"
    raw_text: Optional[str] = None
    metadata: Dict[str, Any] = {}


class ClaimCreate(ClaimBase):
    """Model for creating a new claim"""
    pass


class ClaimInDB(ClaimBase):
    """Claim as stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    is_claim: bool = True
    embedding: Optional[List[float]] = None
    cluster_id: Optional[str] = None
    verdict_id: Optional[str] = None
    status: str = "pending"  # pending, processing, verified, reviewed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


class ClaimResponse(BaseModel):
    """API response model for claims"""
    id: str
    claim_text: str
    source: str
    source_type: str
    entities: List[ClaimEntity]
    claim_type: str
    confidence: float
    status: str
    verdict_summary: Optional[str] = None
    created_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ============ EVIDENCE MODELS ============

class EvidenceSource(BaseModel):
    """Individual evidence source"""
    url: str
    title: str
    excerpt: str = Field(..., max_length=1000)
    published_date: Optional[datetime] = None
    domain: str
    reliability_score: float = Field(ge=0.0, le=1.0)
    source_type: str = "article"  # article, fact-check, government, academic


class EvidenceBase(BaseModel):
    """Base evidence model"""
    claim_id: str
    sources: List[EvidenceSource] = []
    total_sources_found: int = 0
    search_queries: List[str] = []
    retrieval_method: str = "multi-source"


class EvidenceInDB(EvidenceBase):
    """Evidence as stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


# ============ VERDICT MODELS ============

class SourceReference(BaseModel):
    """Source reference in verdict"""
    link: str
    excerpt: str = Field(..., max_length=500)
    title: Optional[str] = None
    reliability: float = Field(ge=0.0, le=1.0)


class VerdictBase(BaseModel):
    """Base verdict model"""
    claim_id: str
    verdict: str = Field(..., regex="^(True|False|Misleading|Unverified|Partially True)$")
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(..., min_length=50, max_length=3000)
    sources: List[SourceReference] = Field(..., min_items=1, max_items=10)
    explain_like_12: str = Field(..., min_length=30, max_length=1000)
    harm_score: int = Field(..., ge=0, le=100)
    recommended_action: str = Field(..., regex="^(label|debunk|escalate|monitor|approve)$")
    expert_explanation: Optional[str] = None
    tags: List[str] = []


class VerdictCreate(VerdictBase):
    """Model for creating a verdict"""
    pass


class VerdictInDB(VerdictBase):
    """Verdict as stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    model_used: str = "gpt-4o"
    processing_time_seconds: float = 0.0
    human_reviewed: bool = False
    reviewer_id: Optional[str] = None
    reviewer_notes: Optional[str] = None
    is_published: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


class VerdictResponse(BaseModel):
    """API response for verdict"""
    id: str
    claim_id: str
    verdict: str
    confidence: float
    reasoning: str
    sources: List[SourceReference]
    explain_like_12: str
    harm_score: int
    recommended_action: str
    human_reviewed: bool
    created_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ============ CLUSTER MODELS ============

class ClusterBase(BaseModel):
    """Claim cluster model"""
    cluster_id: str
    label: str
    claim_ids: List[str] = []
    representative_claim: str
    claim_count: int = 0
    is_trending: bool = False
    trend_score: float = Field(default=0.0, ge=0.0, le=100.0)
    category: str = "general"


class ClusterInDB(ClusterBase):
    """Cluster as stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


# ============ SOURCE RELIABILITY MODELS ============

class SourceReliabilityBase(BaseModel):
    """Source reliability tracking"""
    domain: str
    reliability_rating: float = Field(..., ge=0.0, le=1.0)
    source_category: str = Field(..., regex="^(news|fact-check|government|academic|social|unknown)$")
    verified: bool = False
    bias_rating: Optional[str] = None  # left, center, right
    factual_reporting: Optional[str] = None  # high, medium, low


class SourceReliabilityInDB(SourceReliabilityBase):
    """Source reliability in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    checks_count: int = 0
    last_checked: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# ============ ALERT MODELS ============

class AlertBase(BaseModel):
    """Alert/notification model"""
    alert_type: str = Field(..., regex="^(trending_harm|high_impact|viral_claim|debunk_urgent)$")
    title: str
    description: str
    severity: str = Field(..., regex="^(low|medium|high|critical)$")
    related_claim_ids: List[str] = []
    cluster_id: Optional[str] = None
    is_active: bool = True


class AlertInDB(AlertBase):
    """Alert in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


# ============ FEEDBACK MODELS ============

class FeedbackBase(BaseModel):
    """User feedback/appeal model"""
    claim_id: str
    feedback_type: str = Field(..., regex="^(correction|appeal|additional_evidence|other)$")
    content: str = Field(..., min_length=10, max_length=2000)
    user_email: Optional[EmailStr] = None
    supporting_links: List[str] = []


class FeedbackInDB(FeedbackBase):
    """Feedback in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    status: str = "pending"  # pending, reviewed, accepted, rejected
    reviewed_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


# ============ USER MODELS ============

class UserBase(BaseModel):
    """User/reviewer model"""
    email: EmailStr
    full_name: str
    role: str = Field(default="reviewer", regex="^(admin|reviewer|analyst|viewer)$")
    is_active: bool = True


class UserInDB(UserBase):
    """User in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


# ============ API REQUEST/RESPONSE MODELS ============

class IngestRequest(BaseModel):
    """Request to ingest new text"""
    text: str = Field(..., min_length=10, max_length=10000)
    source: str
    source_type: str = "manual"
    metadata: Dict[str, Any] = {}


class IngestResponse(BaseModel):
    """Response from ingestion"""
    claim_id: Optional[str] = None
    is_claim: bool
    message: str
    claim_detected: Optional[ClaimResponse] = None


class VerifyRequest(BaseModel):
    """Request to verify a claim"""
    claim_id: str
    force_reverify: bool = False


class FilterParams(BaseModel):
    """Common filter parameters"""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)
    claim_type: Optional[str] = None
    verdict: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search_query: Optional[str] = None
