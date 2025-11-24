"""
Tests for consent service
"""
import pytest
import time
from datetime import datetime, timedelta
import jwt

from app.services.consent import consent_service
from app.services.storage import pii_storage
from app.models.schemas import ExtractedPII, ExtractedField
from app.config import settings


class TestConsentService:
    """Tests for consent token creation and validation"""

    def setup_method(self):
        """Setup test data"""
        # Store sample PII
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

    def test_create_consent_token(self):
        """Test creating a consent token"""
        token, expires_at = consent_service.create_consent_token(
            "test_profile", ["full_name", "dob"]
        )

        assert isinstance(token, str)
        assert len(token) > 0
        assert isinstance(expires_at, datetime)
        assert expires_at > datetime.utcnow()

    def test_validate_and_decode_token(self):
        """Test validating and decoding a token"""
        token, _ = consent_service.create_consent_token(
            "test_profile", ["full_name", "address"]
        )

        consent_data = consent_service.validate_and_decode_token(token)

        assert consent_data.profile_id == "test_profile"
        assert "full_name" in consent_data.fields_allowed
        assert "address" in consent_data.fields_allowed

    def test_validate_expired_token(self):
        """Test that expired tokens are rejected"""
        # Create token with very short expiration
        original_expire = settings.consent_token_expire_minutes
        settings.consent_token_expire_minutes = 0

        token, _ = consent_service.create_consent_token("test_profile", ["full_name"])

        # Restore original setting
        settings.consent_token_expire_minutes = original_expire

        # Wait for token to expire
        time.sleep(1)

        with pytest.raises(ValueError, match="expired"):
            consent_service.validate_and_decode_token(token)

    def test_validate_invalid_token(self):
        """Test that invalid tokens are rejected"""
        with pytest.raises(ValueError, match="Invalid"):
            consent_service.validate_and_decode_token("invalid_token")

    def test_validate_tampered_token(self):
        """Test that tampered tokens are rejected"""
        token, _ = consent_service.create_consent_token("test_profile", ["full_name"])

        # Tamper with token
        tampered_token = token[:-5] + "XXXXX"

        with pytest.raises(ValueError):
            consent_service.validate_and_decode_token(tampered_token)

    def test_redeem_consent_token(self):
        """Test redeeming a valid consent token"""
        token, _ = consent_service.create_consent_token(
            "test_profile", ["full_name", "dob"]
        )

        allowed_data = consent_service.redeem_consent_token(token)

        assert "full_name" in allowed_data
        assert allowed_data["full_name"] == "John Doe"
        # 'dob' should map to date_of_birth
        assert "dob" in allowed_data
        assert allowed_data["dob"] == "1990-01-15"

    def test_redeem_token_field_filtering(self):
        """Test that only allowed fields are returned"""
        token, _ = consent_service.create_consent_token(
            "test_profile", ["full_name"]
        )

        allowed_data = consent_service.redeem_consent_token(token)

        assert "full_name" in allowed_data
        assert "address" not in allowed_data
        assert "id_number" not in allowed_data

    def test_redeem_token_nonexistent_profile(self):
        """Test redeeming token for non-existent profile"""
        token, _ = consent_service.create_consent_token(
            "nonexistent_profile", ["full_name"]
        )

        with pytest.raises(ValueError, match="Profile not found"):
            consent_service.redeem_consent_token(token)
