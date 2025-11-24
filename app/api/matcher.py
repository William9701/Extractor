"""
API routes for similarity-based PII matching
"""
from fastapi import APIRouter, HTTPException

from app.models.schemas import MatchRequest, MatchResponse
from app.services.matcher import matcher_service
from app.utils.logger import logger

router = APIRouter(prefix="/match", tags=["matcher"])


@router.post("", response_model=MatchResponse)
async def match_profile(request: MatchRequest) -> MatchResponse:
    """
    Match provided PII against stored profile using embeddings

    Args:
        request: Match request with profile_id, full_name, and address

    Returns:
        Similarity scores and classification (match/no_match/uncertain)
    """
    try:
        logger.info(f"Processing match request for profile_id={request.profile_id}")

        # Perform matching
        name_sim, address_sim, overall, classification = matcher_service.match_profile(
            request.profile_id, request.full_name, request.address
        )

        response = MatchResponse(
            name_similarity=name_sim,
            address_similarity=address_sim,
            overall_score=overall,
            classification=classification,
        )

        return response

    except Exception as e:
        logger.error(f"Match failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Match failed: {str(e)}")
