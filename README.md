# PII Extraction Service

A production-quality Python service for AI-based document data extraction, semantic matching, and secure PII management.

## 🚀 Live Deployment

- **Live API**: https://pii-extraction-service-ohdw.onrender.com
- **API Documentation**: https://pii-extraction-service-ohdw.onrender.com/docs
- **GitHub Repository**: https://github.com/William9701/Extractor
- **Video Demo**: https://www.dropbox.com/scl/fi/xe0tjrrbngzz3skbkf9yj/1124-2.mp4?rlkey=it9lsuyp1s648y4epnqsq0doi&st=t1mo9y13&dl=0

## Features

- **Document PII Extraction**: Extract structured data from documents using Google Gemini (FREE tier)
- **Semantic Matching**: Compare and match PII using embedding-based similarity
- **PDF Form Autofill**: Generate pre-filled PDF forms
- **Consent-Based Sharing**: Secure, time-limited PII access with JWT tokens
- **Semantic Search**: Typeahead-style search with fuzzy matching (bonus feature)

## Architecture

```
app/
├── api/           # FastAPI route handlers
├── services/      # Business logic and AI services
├── models/        # Pydantic schemas
├── utils/         # Utilities (logging, normalization)
└── main.py        # Application entry point

tests/             # Unit and integration tests
templates/         # PDF form templates
```

## Setup

### 1. Prerequisites

- Python 3.9+
- pip

### 2. Installation

```bash
# Clone the repository
git clone git@github.com:William9701/Extractor.git
cd Extractor

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# AI Provider: Google Gemini (FREE tier - 15 requests/min)
GOOGLE_API_KEY=your_google_api_key_here

# Optional: OpenAI as fallback (paid)
OPENAI_API_KEY=your_openai_api_key_here

# Security: Change this in production!
SECRET_KEY=your_secret_key_for_jwt_signing_change_this_in_production

# Optional: Adjust thresholds
NAME_SIMILARITY_THRESHOLD=0.85
ADDRESS_SIMILARITY_THRESHOLD=0.80
OVERALL_MATCH_THRESHOLD=0.82
```

**Important Security Notes:**
- Never commit `.env` file to version control
- Use strong, random `SECRET_KEY` in production
- Rotate keys regularly

## Running the Service

### Development Mode

```bash
# Using uvicorn directly
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the main script
python app/main.py
```

### Production Mode with Gunicorn

```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

The service will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## API Endpoints

### 1. Extract PII from Document

**POST** `/extract`

Extract structured PII from uploaded document using AI.

**Request:**
```bash
# Local
curl -X POST "http://localhost:8000/extract" \
  -F "file=@document.pdf" \
  -F "profile_id=user123" \
  -F "document_type=driver_license"

# Live API
curl -X POST "https://pii-extraction-service-ohdw.onrender.com/extract" \
  -F "file=@document.pdf" \
  -F "profile_id=user123" \
  -F "document_type=driver_license"
```

**Response:**
```json
{
  "profile_id": "user123",
  "document_type": "driver_license",
  "fields": {
    "full_name": {
      "value": "John Doe",
      "confidence": 0.95
    },
    "date_of_birth": {
      "value": "1990-01-15",
      "confidence": 0.90
    },
    "address": {
      "value": "123 Main Street, San Jose CA 95110",
      "confidence": 0.85
    },
    "id_number": {
      "value": "DL12345678",
      "confidence": 0.95
    },
    "expiry_date": {
      "value": "2028-01-15",
      "confidence": 0.90
    }
  },
  "extracted_at": "2025-01-15T10:30:00Z"
}
```

### 2. Match PII Using Similarity

**POST** `/match`

Compare provided PII against stored data using embeddings.

**Request:**
```bash
curl -X POST "http://localhost:8000/match" \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": "user123",
    "full_name": "John Doe",
    "address": "123 Main St, San Jose CA"
  }'
```

**Response:**
```json
{
  "name_similarity": 0.98,
  "address_similarity": 0.92,
  "overall_score": 0.95,
  "classification": "match"
}
```

Classifications: `"match"`, `"no_match"`, or `"uncertain"`

### 3. Generate Pre-filled PDF

**POST** `/prefill-pdf`

Fill a PDF form with provided data.

**Request:**
```bash
curl -X POST "http://localhost:8000/prefill-pdf" \
  -H "Content-Type: application/json" \
  -d '{
    "form_type": "sample_form",
    "fields": {
      "full_name": "Jane Smith",
      "dob": "1985-05-20",
      "address": "456 Oak Ave",
      "id_number": "DL87654321"
    }
  }' \
  --output filled_form.pdf
```

Returns a PDF file.

### 4. Create Consent Token

**POST** `/consent/create`

Generate a time-limited token for secure PII access.

**Request:**
```bash
curl -X POST "http://localhost:8000/consent/create" \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": "user123",
    "fields_allowed": ["full_name", "dob"]
  }'
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2025-01-15T10:45:00Z"
}
```

Token expires in 15 minutes (configurable).

### 5. Redeem Consent Token

**GET** `/consent/redeem?token={token}`

Retrieve allowed fields using a consent token.

**Request:**
```bash
curl "http://localhost:8000/consent/redeem?token=eyJhbGci..."
```

**Response:**
```json
{
  "full_name": "John Doe",
  "dob": "1990-01-15"
}
```

Only returns fields specified in the token. Returns 401 if token is expired or invalid.

### 6. Semantic Search (Bonus)

**GET** `/search?query={query}&limit={limit}`

Search profiles using semantic similarity.

**Request:**
```bash
curl "http://localhost:8000/search?query=John&limit=5"
```

**Response:**
```json
{
  "query": "John",
  "results": [
    {
      "profile_id": "user123",
      "full_name": "John Doe",
      "address": "123 Main Street, San Jose CA",
      "similarity_score": 0.95
    }
  ]
}
```

Supports partial, fuzzy, and semantic matching.

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_consent.py

# Run with verbose output
pytest -v
```

Test coverage includes:
- Normalization utilities
- Embedding generation and similarity
- Consent token creation and validation
- API endpoints (integration tests)

## Data Normalization

All extracted fields are automatically normalized:

- **Dates**: Converted to `YYYY-MM-DD` format
- **Names**: Title case with proper spacing
- **Addresses**: Standardized abbreviations (St→Street, Ave→Avenue)
- **ID Numbers**: Alphanumeric only, uppercase

## Security Features

### PII Protection
- PII never written to logs (automatically redacted)
- Structured logging with sanitization
- In-memory storage (no persistent PII)

### Consent Tokens
- Signed with HMAC (JWT)
- Time-limited (15 minutes default)
- Field-level access control
- Tamper-proof validation

### API Security
- Input validation with Pydantic
- Type-safe request/response schemas
- Graceful error handling
- No information leakage in errors

## Logging

The service uses structured JSON logging:

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "INFO",
  "logger": "pii_service",
  "message": "Extraction completed successfully",
  "profile_id": "user123"
}
```

PII fields are automatically redacted from logs.

## Configuration Options

Environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google Gemini API key (FREE tier) | Required |
| `OPENAI_API_KEY` | OpenAI API key (fallback, paid) | Optional |
| `SECRET_KEY` | JWT signing key | Must change in production |
| `CONSENT_TOKEN_EXPIRE_MINUTES` | Token expiration time | 15 |
| `NAME_SIMILARITY_THRESHOLD` | Name match threshold | 0.85 |
| `ADDRESS_SIMILARITY_THRESHOLD` | Address match threshold | 0.80 |
| `OVERALL_MATCH_THRESHOLD` | Overall match threshold | 0.82 |
| `LOG_LEVEL` | Logging level | INFO |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |

## Assumptions

1. **AI Provider**: Uses Google Gemini (FREE tier: 15 requests/min, 1M requests/month) by default. Falls back to OpenAI if available. Get a free API key at https://makersuite.google.com/app/apikey

2. **Storage**: In-memory storage for demo purposes. In production, use:
   - PostgreSQL/MongoDB for PII data
   - Vector database (Pinecone, Weaviate) for embeddings
   - Redis for session/cache management

3. **Document Formats**: Currently supports PDF and image files. Extraction quality depends on document clarity.

4. **Embedding Model**: Uses lightweight character frequency + sequence matching algorithm (optimized for Render free tier 512MB RAM limit).

5. **PDF Templates**: Generates simple forms if template doesn't exist. In production, use proper PDF form templates with field mappings.

## Limitations

1. **Extraction Accuracy**: Depends on:
   - Document quality (resolution, clarity)
   - LLM capabilities and prompting
   - Document format standardization

2. **Scalability**:
   - In-memory storage limits to single instance
   - No distributed processing
   - Synchronous extraction (no queue system)

3. **Security**:
   - No authentication/authorization layer
   - No rate limiting
   - No audit logging for compliance

4. **PDF Handling**:
   - Basic form filling only
   - Limited support for complex PDF forms
   - No digital signature support

## Production Considerations

For production deployment:

1. **Database**: Replace in-memory storage with PostgreSQL + pgvector
2. **Queue System**: Add Celery/RQ for async processing
3. **Authentication**: Implement OAuth2/API keys
4. **Rate Limiting**: Add Redis-based rate limiting
5. **Monitoring**: Integrate Prometheus/Grafana
6. **Audit Logs**: Store all PII access for compliance
7. **Encryption**: Encrypt PII at rest and in transit
8. **Backup**: Regular backups of PII data
9. **GDPR Compliance**: Data retention policies and deletion
10. **CI/CD**: Automated testing and deployment pipeline

## Development

### Project Structure
```
.
├── app/
│   ├── api/              # API route handlers
│   │   ├── extraction.py
│   │   ├── matcher.py
│   │   ├── pdf.py
│   │   ├── consent.py
│   │   └── search.py
│   ├── services/         # Business logic
│   │   ├── extractor.py
│   │   ├── embeddings.py
│   │   ├── matcher.py
│   │   ├── pdf_service.py
│   │   ├── consent.py
│   │   ├── search.py
│   │   └── storage.py
│   ├── models/           # Data models
│   │   └── schemas.py
│   ├── utils/            # Utilities
│   │   ├── logger.py
│   │   └── normalizer.py
│   ├── config.py         # Configuration
│   └── main.py           # App entry point
├── tests/                # Test suite
├── templates/            # PDF templates
├── requirements.txt      # Dependencies
├── .env.example          # Config template
├── .gitignore
└── README.md
```

### Adding New Features

1. **New Extraction Fields**: Update `ExtractedPII` model in [models/schemas.py](app/models/schemas.py)
2. **New Document Types**: Add to `DocumentType` enum
3. **Custom Embeddings**: Modify `EmbeddingService` in [services/embeddings.py](app/services/embeddings.py)
4. **New APIs**: Add router in `app/api/` and include in [main.py](app/main.py)

## Troubleshooting

### Common Issues

**Issue**: `GOOGLE_API_KEY not configured`
- **Solution**: Get a free API key at https://makersuite.google.com/app/apikey and add `GOOGLE_API_KEY` to `.env` file

**Issue**: PDF generation fails
- **Solution**: Check that `templates/` directory exists and is writable

**Issue**: Tests failing
- **Solution**: Run `pytest -v` to see detailed errors. Ensure all dependencies installed.

## License

MIT License

## Support

For issues or questions:
- Create an issue in the repository
- Check API documentation at `/docs`
- Review test cases for usage examples

## Authors

Built as a technical assessment for Python AI Engineer position.
