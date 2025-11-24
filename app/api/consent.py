"""
API routes for consent-based PII sharing
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.models.schemas import ConsentCreateRequest, ConsentCreateResponse
from app.services.consent import consent_service
from app.utils.logger import logger

router = APIRouter(prefix="/consent", tags=["consent"])


@router.post("/create", response_model=ConsentCreateResponse)
async def create_consent_token(request: ConsentCreateRequest) -> ConsentCreateResponse:
    """
    Create a signed, time-limited consent token

    Args:
        request: Profile ID and list of allowed fields

    Returns:
        Consent token and expiration timestamp
    """
    try:
        logger.info(
            f"Creating consent token for profile_id={request.profile_id}, "
            f"fields={request.fields_allowed}"
        )

        token, expires_at = consent_service.create_consent_token(
            request.profile_id, request.fields_allowed
        )

        return ConsentCreateResponse(token=token, expires_at=expires_at)

    except Exception as e:
        logger.error(f"Failed to create consent token: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create consent token: {str(e)}"
        )


@router.get("/redeem")
async def redeem_consent_token(token: str = Query(...)) -> JSONResponse:
    """
    Redeem a consent token and retrieve allowed fields

    Args:
        token: JWT consent token

    Returns:
        Dictionary with only the allowed PII fields
    """
    try:
        logger.info("Processing consent token redemption")

        # Redeem token
        allowed_data = consent_service.redeem_consent_token(token)

        return JSONResponse(content=allowed_data)

    except ValueError as e:
        logger.warning(f"Invalid consent token: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to redeem consent token: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to redeem consent token: {str(e)}"
        )
