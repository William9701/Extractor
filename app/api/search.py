"""
API routes for semantic search (bonus feature)
"""
from fastapi import APIRouter, Query
from typing import List

from app.models.schemas import SearchResponse, SearchResult
from app.services.search import search_service
from app.utils.logger import logger

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
async def search_profiles(
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(5, ge=1, le=20, description="Maximum number of results"),
) -> SearchResponse:
    """
    Semantic search for profiles (typeahead-style)

    Supports:
    - Partial matching
    - Fuzzy matching
    - Semantic similarity

    Args:
        query: Search query string
        limit: Maximum number of results (default: 5)

    Returns:
        List of matching profiles ranked by similarity
    """
    logger.info(f"Processing search query: '{query}', limit={limit}")

    results = search_service.search_profiles(query, limit)

    return SearchResponse(query=query, results=results)
