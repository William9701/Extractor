# Quick Start Guide

Get the PII Extraction Service running in 5 minutes.

## Prerequisites

- Python 3.9 or higher
- pip
- (Optional) OpenAI API key for real document extraction

## Step 1: Clone and Setup

```bash
# Navigate to project directory
cd Extractor

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env and add your OpenAI API key (optional)
# If you skip this step, the service will use mock data
```

Example `.env`:
```env
OPENAI_API_KEY=sk-your-key-here
SECRET_KEY=change-this-to-a-random-string
```

## Step 3: Run the Service

```bash
# Start the development server
python app/main.py
```

You should see:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 4: Test the API

Open your browser and visit:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

Or use the manual test script:
```bash
python test_api_manual.py
```

## Step 5: Try the Endpoints

### Using the Interactive Docs (http://localhost:8000/docs)

1. **Extract PII**:
   - Click on `POST /extract`
   - Click "Try it out"
   - Upload an image or PDF
   - Fill in `profile_id`: "user123"
   - Fill in `document_type`: "driver_license"
   - Click "Execute"

2. **Match PII**:
   - Click on `POST /match`
   - Click "Try it out"
   - Use the same `profile_id` from step 1
   - Enter a name and address to match
   - Click "Execute"

3. **Generate PDF**:
   - Click on `POST /prefill-pdf`
   - Click "Try it out"
   - Fill in the form fields
   - Click "Execute"
   - Download the generated PDF

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Create consent token
curl -X POST http://localhost:8000/consent/create \
  -H "Content-Type: application/json" \
  -d '{"profile_id": "user123", "fields_allowed": ["full_name", "dob"]}'

# Search
curl "http://localhost:8000/search?query=John&limit=5"
```

## Step 6: Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# View coverage report
# Open htmlcov/index.html in your browser
```

## Common Issues

### Issue: Import errors
**Solution**: Make sure you're in the virtual environment
```bash
# Check if activated (you should see (venv) in your prompt)
which python  # Should point to venv/bin/python
```

### Issue: Port 8000 already in use
**Solution**: Use a different port
```bash
python -m uvicorn app.main:app --port 8001
```

### Issue: OpenAI API errors
**Solution**: The service works without an API key (uses mock data)
- For testing, you don't need a real API key
- For production, add `OPENAI_API_KEY` to `.env`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Explore API endpoints at http://localhost:8000/docs
- Run the test suite to understand the code

## Quick Reference

### Start Server
```bash
python app/main.py
```

### Run Tests
```bash
pytest
```

### Generate PDF
```bash
curl -X POST http://localhost:8000/prefill-pdf \
  -H "Content-Type: application/json" \
  -d '{"form_type": "sample_form", "fields": {"full_name": "John Doe"}}' \
  --output form.pdf
```

### Docker (Alternative)
```bash
docker-compose up
```

## Production Deployment

### Using Gunicorn
```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Using Docker
```bash
docker build -t pii-service .
docker run -p 8000:8000 --env-file .env pii-service
```

### Deploy to Render
1. Push code to GitHub
2. Connect repository to Render
3. Render will auto-detect `render.yaml`
4. Add environment variables in Render dashboard
5. Deploy!

## Need Help?

- Check the logs in the console
- Visit http://localhost:8000/docs for API documentation
- Review test cases in `tests/` directory
- See example usage in `test_api_manual.py`
