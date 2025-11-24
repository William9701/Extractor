"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Supported document types"""
    DRIVER_LICENSE = "driver_license"
    PASSPORT = "passport"
    ID_CARD = "id_card"
    OTHER = "other"


class ExtractedField(BaseModel):
    """Single extracted field with confidence"""
    value: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)


class ExtractedPII(BaseModel):
    """Structured PII data extracted from document"""
    full_name: ExtractedField
    date_of_birth: ExtractedField
    address: ExtractedField
    id_number: ExtractedField
    expiry_date: ExtractedField


class ExtractionRequest(BaseModel):
    """Metadata for extraction request"""
    profile_id: str
    document_type: DocumentType


class ExtractionResponse(BaseModel):
    """Response from extraction API"""
    profile_id: str
    document_type: str
    fields: ExtractedPII
    extracted_at: datetime = Field(default_factory=datetime.utcnow)


class MatchRequest(BaseModel):
    """Request for similarity matching"""
    profile_id: str
    full_name: str
    address: str


class MatchResult(str, Enum):
    """Match classification"""
    MATCH = "match"
    NO_MATCH = "no_match"
    UNCERTAIN = "uncertain"


class MatchResponse(BaseModel):
    """Response from matcher API"""
    name_similarity: float = Field(ge=0.0, le=1.0)
    address_similarity: float = Field(ge=0.0, le=1.0)
    overall_score: float = Field(ge=0.0, le=1.0)
    classification: MatchResult


class PDFPrefillRequest(BaseModel):
    """Request for PDF autofill"""
    form_type: str
    fields: Dict[str, str]


class ConsentCreateRequest(BaseModel):
    """Request to create consent token"""
    profile_id: str
    fields_allowed: List[str]


class ConsentCreateResponse(BaseModel):
    """Response with consent token"""
    token: str
    expires_at: datetime


class ConsentData(BaseModel):
    """Decoded consent token data"""
    profile_id: str
    fields_allowed: List[str]
    exp: int


class SearchResult(BaseModel):
    """Single search result"""
    profile_id: str
    full_name: str
    address: str
    similarity_score: float


class SearchResponse(BaseModel):
    """Response from search endpoint"""
    query: str
    results: List[SearchResult]
