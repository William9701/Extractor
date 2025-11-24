"""
Pytest configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def sample_pii_data():
    """Sample PII data for testing"""
    return {
        "profile_id": "test_profile_123",
        "full_name": "John Doe",
        "date_of_birth": "1990-01-15",
        "address": "123 Main Street, San Jose CA 95110",
        "id_number": "DL12345678",
    }


@pytest.fixture
def sample_fields():
    """Sample fields for PDF generation"""
    return {
        "full_name": "Jane Smith",
        "dob": "1985-05-20",
        "address": "456 Oak Avenue, San Francisco CA 94102",
        "id_number": "DL87654321",
    }
