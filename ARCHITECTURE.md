# Architecture Documentation

## System Overview

The PII Extraction Service is designed as a microservice architecture with clear separation of concerns.

## Architecture Diagram

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP/REST
       │
┌──────▼──────────────────────────────────────┐
│          FastAPI Application                │
│  ┌────────────────────────────────────────┐ │
│  │        API Layer (Routes)              │ │
│  │  - extraction.py                       │ │
│  │  - matcher.py                          │ │
│  │  - pdf.py                              │ │
│  │  - consent.py                          │ │
│  │  - search.py                           │ │
│  └─────────────┬──────────────────────────┘ │
│                │                            │
│  ┌─────────────▼──────────────────────────┐ │
│  │      Service Layer (Business Logic)    │ │
│  │  - extractor.py    (LLM extraction)    │ │
│  │  - embeddings.py   (Vector generation) │ │
│  │  - matcher.py      (Similarity calc)   │ │
│  │  - pdf_service.py  (PDF generation)    │ │
│  │  - consent.py      (Token management)  │ │
│  │  - search.py       (Semantic search)   │ │
│  │  - storage.py      (Data persistence)  │ │
│  └─────────────┬──────────────────────────┘ │
│                │                            │
│  ┌─────────────▼──────────────────────────┐ │
│  │       Utility Layer                    │ │
│  │  - logger.py       (Structured logs)   │ │
│  │  - normalizer.py   (Data cleaning)     │ │
│  └────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
       │              │              │
       │              │              │
   ┌───▼───┐     ┌────▼────┐    ┌───▼────┐
   │ OpenAI│     │Sentence │    │ Local  │
   │  API  │     │Transform│    │Storage │
   └───────┘     └─────────┘    └────────┘
```

## Component Details

### 1. API Layer (`app/api/`)

**Responsibility**: HTTP request handling and validation

- **extraction.py**: Document upload and PII extraction endpoint
- **matcher.py**: Similarity matching endpoint
- **pdf.py**: PDF form generation endpoint
- **consent.py**: Consent token creation and redemption
- **search.py**: Semantic search endpoint

**Key Features**:
- Request validation using Pydantic
- Error handling and HTTP status codes
- Input sanitization
- Response serialization

### 2. Service Layer (`app/services/`)

**Responsibility**: Business logic and core functionality

#### extractor.py - Document Extraction
- Interfaces with OpenAI GPT-4 Vision
- Handles image preprocessing
- Parses LLM responses
- Normalizes extracted data

```python
# Flow:
Image Upload → Base64 Encoding → GPT-4 Vision → JSON Parsing → Normalization → Storage
```

#### embeddings.py - Vector Generation
- Uses Sentence Transformers (all-MiniLM-L6-v2)
- Generates 384-dimensional embeddings
- Calculates cosine similarity
- Thread-safe operations

#### matcher.py - Similarity Matching
- Compares embeddings using cosine similarity
- Implements weighted scoring (name: 60%, address: 40%)
- Classifies matches based on thresholds
- Handles edge cases (missing data, etc.)

#### pdf_service.py - PDF Generation
- Fills existing PDF forms using PyPDF2
- Falls back to generating simple PDFs with ReportLab
- Handles field mapping
- Returns downloadable PDFs

#### consent.py - Token Management
- Creates signed JWT tokens
- Validates signatures and expiration
- Implements field-level access control
- Prevents token tampering

#### search.py - Semantic Search
- Searches across all stored profiles
- Uses embedding similarity for ranking
- Supports fuzzy and partial matching
- Implements result limiting

#### storage.py - Data Persistence
- Thread-safe in-memory storage
- Stores PII and embeddings
- Provides CRUD operations
- Designed for easy replacement with database

### 3. Model Layer (`app/models/`)

**Responsibility**: Data schemas and validation

- **schemas.py**: Pydantic models for all data structures
  - Request/Response models
  - Domain models
  - Enums for constants

**Benefits**:
- Type safety
- Automatic validation
- API documentation generation
- Serialization/deserialization

### 4. Utility Layer (`app/utils/`)

**Responsibility**: Cross-cutting concerns

#### logger.py
- Structured JSON logging
- PII redaction
- Log level management
- Centralized logging configuration

#### normalizer.py
- Date normalization (→ YYYY-MM-DD)
- Name normalization (→ Title Case)
- Address standardization
- ID number cleaning

### 5. Configuration (`app/config.py`)

**Responsibility**: Environment management

- Loads environment variables
- Provides type-safe configuration
- Validates required settings
- Supports multiple environments

## Data Flow

### Extraction Flow

```
1. Client uploads document (PDF/Image)
   ↓
2. API validates request (file size, type, metadata)
   ↓
3. ExtractionService converts image to base64
   ↓
4. Send to GPT-4 Vision with structured prompt
   ↓
5. Parse JSON response from LLM
   ↓
6. Normalize all fields (dates, names, addresses)
   ↓
7. Store PII in memory
   ↓
8. Generate embeddings for name and address
   ↓
9. Store embeddings in memory
   ↓
10. Return structured response to client
```

### Matching Flow

```
1. Client sends profile_id + data to match
   ↓
2. API validates request
   ↓
3. Retrieve stored embeddings for profile_id
   ↓
4. Generate embeddings for input data
   ↓
5. Calculate cosine similarity for name and address
   ↓
6. Compute weighted overall score
   ↓
7. Classify result (match/no_match/uncertain)
   ↓
8. Return similarity scores and classification
```

### Consent Flow

```
CREATE:
1. Client requests token with profile_id + allowed_fields
   ↓
2. Create JWT payload with expiration (15 min)
   ↓
3. Sign token with SECRET_KEY
   ↓
4. Return token + expiration timestamp

REDEEM:
1. Client provides token
   ↓
2. Verify signature
   ↓
3. Check expiration
   ↓
4. Decode payload to get profile_id + allowed_fields
   ↓
5. Retrieve PII from storage
   ↓
6. Filter to only allowed fields
   ↓
7. Return filtered data (no leakage)
```

## Security Architecture

### 1. PII Protection

```
┌──────────────────────────────────────────┐
│          PII Protection Layers           │
├──────────────────────────────────────────┤
│ 1. Input Validation (Pydantic)          │
│ 2. No PII in Logs (Sanitization)        │
│ 3. In-Memory Only (No disk writes)      │
│ 4. Field-Level Access (Consent tokens)  │
│ 5. Time-Limited Access (JWT expiration) │
└──────────────────────────────────────────┘
```

### 2. Token Security

- **Signing**: HMAC-SHA256 with SECRET_KEY
- **Expiration**: 15 minutes (configurable)
- **Payload**: Minimal data (profile_id, fields, timestamps)
- **Validation**: Strict signature and expiration checks

### 3. API Security

- **Input Validation**: All requests validated with Pydantic
- **Error Handling**: No information leakage in errors
- **Type Safety**: Python type hints throughout
- **Logging**: Structured logs with PII redaction

## Scalability Considerations

### Current Architecture

- Single instance
- In-memory storage
- Synchronous processing
- No queue system

**Limitations**:
- Memory constraints
- No horizontal scaling
- No failover
- No persistence

### Production Architecture (Recommended)

```
┌─────────────┐
│Load Balancer│
└──────┬──────┘
       │
   ┌───┴────┐
   │        │
┌──▼──┐  ┌──▼──┐
│API  │  │API  │  (Multiple instances)
│Node │  │Node │
└──┬──┘  └──┬──┘
   │        │
   └───┬────┘
       │
   ┌───▼────────────────┐
   │                    │
┌──▼────┐  ┌───▼───┐  ┌▼────┐
│Postgres│  │ Redis │  │Queue│
│+Vector │  │ Cache │  │(RQ) │
└────────┘  └───────┘  └─────┘
```

**Changes Needed**:
1. Replace `storage.py` with PostgreSQL + pgvector
2. Add Redis for caching and rate limiting
3. Add task queue (Celery/RQ) for async extraction
4. Add API authentication (OAuth2/JWT)
5. Add rate limiting middleware
6. Add distributed tracing (OpenTelemetry)

## Testing Architecture

### Test Pyramid

```
        ┌────────┐
        │  E2E   │  (API integration tests)
        └────────┘
     ┌──────────────┐
     │ Integration  │  (Service tests)
     └──────────────┘
  ┌──────────────────────┐
  │     Unit Tests       │  (Utils, models)
  └──────────────────────┘
```

### Test Coverage

- **Unit Tests**: Normalizers, embeddings, utilities
- **Service Tests**: Consent logic, matching logic
- **Integration Tests**: API endpoints, full flows

### Mocking Strategy

- Mock LLM calls in tests (expensive)
- Use real embedding model (lightweight)
- In-memory storage (no mocking needed)

## Deployment Options

### 1. Docker (Recommended)

```bash
docker-compose up
```

Benefits:
- Consistent environment
- Easy scaling
- Isolated dependencies

### 2. Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pii-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pii-service
  template:
    spec:
      containers:
      - name: pii-service
        image: pii-service:latest
        ports:
        - containerPort: 8000
```

### 3. Serverless (Cloud Functions)

- Not recommended due to:
  - Cold start latency
  - Model loading overhead
  - Stateful embeddings

## Monitoring & Observability

### Recommended Stack

1. **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
2. **Metrics**: Prometheus + Grafana
3. **Tracing**: Jaeger / OpenTelemetry
4. **Alerting**: PagerDuty / Opsgenie

### Key Metrics to Track

- Request rate, latency, error rate
- LLM API call latency and costs
- Embedding generation time
- Storage usage
- Token validation failures
- Match result distribution

## Future Enhancements

### Short Term
1. Add more document types (passport, ID card)
2. Support multiple AI providers
3. Batch processing API
4. Webhook notifications

### Long Term
1. Multi-language support
2. OCR preprocessing
3. Document verification (fraud detection)
4. Audit trail and compliance reporting
5. GDPR compliance features (data deletion, export)
6. Advanced search (filters, sorting)
7. Real-time updates (WebSocket)

## Code Quality Standards

### Principles
- SOLID principles
- DRY (Don't Repeat Yourself)
- KISS (Keep It Simple, Stupid)
- Separation of concerns
- Dependency injection

### Style Guide
- PEP 8 compliant
- Type hints throughout
- Docstrings for all public functions
- Meaningful variable names
- Comments for complex logic

### Code Review Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No PII in logs
- [ ] Error handling present
- [ ] Type hints added
- [ ] Security implications considered
