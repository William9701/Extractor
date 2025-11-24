"""
API integration tests
"""
import pytest
from io import BytesIO
from PIL import Image

from app.services.storage import pii_storage
from app.models.schemas import ExtractedPII, ExtractedField


class TestExtractionAPI:
    """Tests for extraction endpoint"""

    def test_extract_endpoint_missing_file(self, client):
        """Test extraction with missing file"""
        response = client.post(
            "/extract",
            data={"profile_id": "test123", "document_type": "driver_license"},
        )

        assert response.status_code == 422  # Validation error

    def test_extract_endpoint_invalid_document_type(self, client):
        """Test extraction with invalid document type"""
        # Create dummy image
        img = Image.new("RGB", (100, 100), color="white")
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        response = client.post(
            "/extract",
            files={"file": ("test.png", img_bytes, "image/png")},
            data={"profile_id": "test123", "document_type": "invalid_type"},
        )

        assert response.status_code == 400


class TestMatcherAPI:
    """Tests for matcher endpoint"""

    def setup_method(self):
        """Setup test data"""
        from app.services.embeddings import embedding_service

        # Store test PII
        pii = ExtractedPII(
            full_name=ExtractedField(value="John Doe", confidence=0.95),
            date_of_birth=ExtractedField(value="1990-01-15", confidence=0.90),
            address=ExtractedField(
                value="123 Main Street, San Jose CA", confidence=0.85
            ),
            id_number=ExtractedField(value="DL12345678", confidence=0.95),
            expiry_date=ExtractedField(value="2028-01-15", confidence=0.90),
        )
        pii_storage.store_pii("test_profile", pii)

        # Store embeddings
        name_emb = embedding_service.generate_embedding("John Doe")
        addr_emb = embedding_service.generate_embedding("123 Main Street, San Jose CA")
        pii_storage.store_embeddings("test_profile", name_emb, addr_emb)

    def test_match_endpoint_exact_match(self, client):
        """Test matching with exact data"""
        response = client.post(
            "/match",
            json={
                "profile_id": "test_profile",
                "full_name": "John Doe",
                "address": "123 Main Street, San Jose CA",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert "name_similarity" in data
        assert "address_similarity" in data
        assert "overall_score" in data
        assert "classification" in data
        assert data["classification"] in ["match", "no_match", "uncertain"]

    def test_match_endpoint_no_profile(self, client):
        """Test matching with non-existent profile"""
        response = client.post(
            "/match",
            json={
                "profile_id": "nonexistent",
                "full_name": "John Doe",
                "address": "123 Main Street",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["classification"] == "no_match"


class TestPDFAPI:
    """Tests for PDF generation endpoint"""

    def test_prefill_pdf_endpoint(self, client, sample_fields):
        """Test PDF generation"""
        response = client.post(
            "/prefill-pdf", json={"form_type": "sample_form", "fields": sample_fields}
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert len(response.content) > 0


class TestConsentAPI:
    """Tests for consent endpoints"""

    def setup_method(self):
        """Setup test data"""
        pii = ExtractedPII(
            full_name=ExtractedField(value="John Doe", confidence=0.95),
            date_of_birth=ExtractedField(value="1990-01-15", confidence=0.90),
            address=ExtractedField(value="123 Main Street", confidence=0.85),
            id_number=ExtractedField(value="DL12345678", confidence=0.95),
            expiry_date=ExtractedField(value="2028-01-15", confidence=0.90),
        )
        pii_storage.store_pii("test_profile", pii)

    def test_create_consent_token(self, client):
        """Test consent token creation"""
        response = client.post(
            "/consent/create",
            json={"profile_id": "test_profile", "fields_allowed": ["full_name", "dob"]},
        )

        assert response.status_code == 200
        data = response.json()

        assert "token" in data
        assert "expires_at" in data
        assert len(data["token"]) > 0

    def test_redeem_consent_token(self, client):
        """Test consent token redemption"""
        # Create token
        create_response = client.post(
            "/consent/create",
            json={"profile_id": "test_profile", "fields_allowed": ["full_name"]},
        )

        token = create_response.json()["token"]

        # Redeem token
        redeem_response = client.get(f"/consent/redeem?token={token}")

        assert redeem_response.status_code == 200
        data = redeem_response.json()

        assert "full_name" in data
        assert data["full_name"] == "John Doe"

    def test_redeem_invalid_token(self, client):
        """Test redemption with invalid token"""
        response = client.get("/consent/redeem?token=invalid_token")

        assert response.status_code == 401


class TestSearchAPI:
    """Tests for search endpoint"""

    def test_search_endpoint(self, client):
        """Test search endpoint"""
        response = client.get("/search?query=John")

        assert response.status_code == 200
        data = response.json()

        assert "query" in data
        assert "results" in data
        assert isinstance(data["results"], list)

    def test_search_endpoint_empty_query(self, client):
        """Test search with empty query"""
        response = client.get("/search?query=")

        assert response.status_code == 422  # Validation error


class TestHealthEndpoints:
    """Tests for health and root endpoints"""

    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert "service" in data
        assert "version" in data
        assert "endpoints" in data

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
