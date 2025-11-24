"""
Consent-based PII sharing service with JWT tokens
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import jwt

from app.config import settings
from app.models.schemas import ConsentData
from app.services.storage import pii_storage
from app.utils.logger import logger


class ConsentService:
    """Service for managing consent-based PII sharing"""

    def create_consent_token(
        self, profile_id: str, fields_allowed: List[str]
    ) -> tuple[str, datetime]:
        """
        Create a signed, time-limited consent token

        Args:
            profile_id: Profile ID to grant access to
            fields_allowed: List of field names that can be accessed

        Returns:
            Tuple of (token, expiration_datetime)
        """
        # Calculate expiration
        expires_at = datetime.utcnow() + timedelta(
            minutes=settings.consent_token_expire_minutes
        )

        # Create payload
        payload = {
            "profile_id": profile_id,
            "fields_allowed": fields_allowed,
            "exp": int(expires_at.timestamp()),
            "iat": int(datetime.utcnow().timestamp()),
        }

        # Sign token
        token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

        logger.info(
            f"Created consent token for profile_id={profile_id}, "
            f"fields={len(fields_allowed)}, expires={expires_at.isoformat()}"
        )

        return token, expires_at

    def validate_and_decode_token(self, token: str) -> ConsentData:
        """
        Validate and decode a consent token

        Args:
            token: JWT token string

        Returns:
            ConsentData object with decoded information

        Raises:
            ValueError: If token is invalid or expired
        """
        try:
            # Decode and verify token
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )

            consent_data = ConsentData(
                profile_id=payload["profile_id"],
                fields_allowed=payload["fields_allowed"],
                exp=payload["exp"],
            )

            logger.info(f"Validated consent token for profile_id={consent_data.profile_id}")

            return consent_data

        except jwt.ExpiredSignatureError:
            logger.warning("Consent token has expired")
            raise ValueError("Consent token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid consent token: {str(e)}")
            raise ValueError(f"Invalid consent token: {str(e)}")

    def redeem_consent_token(self, token: str) -> Dict[str, Any]:
        """
        Redeem a consent token and return allowed fields

        Args:
            token: JWT token string

        Returns:
            Dictionary with allowed fields only

        Raises:
            ValueError: If token is invalid, expired, or profile not found
        """
        # Validate token
        consent_data = self.validate_and_decode_token(token)

        # Get PII data
        pii = pii_storage.get_pii(consent_data.profile_id)

        if not pii:
            logger.error(f"Profile not found: {consent_data.profile_id}")
            raise ValueError("Profile not found")

        # Filter fields based on consent
        allowed_data = {}

        field_mapping = {
            "full_name": pii.full_name.value,
            "date_of_birth": pii.date_of_birth.value,
            "dob": pii.date_of_birth.value,
            "address": pii.address.value,
            "id_number": pii.id_number.value,
            "expiry_date": pii.expiry_date.value,
        }

        for field in consent_data.fields_allowed:
            if field in field_mapping:
                allowed_data[field] = field_mapping[field]
            else:
                logger.warning(f"Unknown field requested: {field}")

        logger.info(
            f"Redeemed consent token for profile_id={consent_data.profile_id}, "
            f"returned {len(allowed_data)} fields"
        )

        return allowed_data


# Global service instance
consent_service = ConsentService()
