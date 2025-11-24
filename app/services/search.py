"""
Semantic search service for typeahead functionality
"""
from typing import List, Tuple
from app.services.embeddings import embedding_service
from app.services.storage import pii_storage
from app.models.schemas import SearchResult
from app.utils.logger import logger


class SearchService:
    """Service for semantic search across stored profiles"""

    def search_profiles(self, query: str, limit: int = 5) -> List[SearchResult]:
        """
        Search for profiles using semantic similarity

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of SearchResult objects sorted by similarity
        """
        if not query or not query.strip():
            return []

        # Generate query embedding
        query_embedding = embedding_service.generate_embedding(query)

        # Get all stored profiles and embeddings
        all_embeddings = pii_storage.get_all_embeddings()

        if not all_embeddings:
            logger.info("No profiles available for search")
            return []

        # Calculate similarities for all profiles
        results: List[Tuple[str, float]] = []

        for profile_id, embeddings in all_embeddings.items():
            # Calculate similarity against both name and address
            name_sim = embedding_service.calculate_similarity(
                query_embedding, embeddings["name"]
            )
            address_sim = embedding_service.calculate_similarity(
                query_embedding, embeddings["address"]
            )

            # Use the maximum similarity (query could match either)
            max_similarity = max(name_sim, address_sim)

            results.append((profile_id, max_similarity))

        # Sort by similarity (descending)
        results.sort(key=lambda x: x[1], reverse=True)

        # Get top results
        top_results = results[:limit]

        # Build SearchResult objects
        search_results = []

        for profile_id, similarity in top_results:
            # Only include if similarity is above threshold (0.3 for fuzzy matching)
            if similarity < 0.3:
                continue

            pii = pii_storage.get_pii(profile_id)
            if pii:
                search_results.append(
                    SearchResult(
                        profile_id=profile_id,
                        full_name=pii.full_name.value or "",
                        address=pii.address.value or "",
                        similarity_score=similarity,
                    )
                )

        logger.info(f"Search query '{query}' returned {len(search_results)} results")

        return search_results


# Global service instance
search_service = SearchService()
