"""
Similarity-based PII matching service
"""
from typing import Tuple
from app.config import settings
from app.models.schemas import MatchResult
from app.services.embeddings import embedding_service
from app.services.storage import pii_storage
from app.utils.logger import logger


class MatcherService:
    """Service for matching PII using embedding similarity"""

    def match_profile(
        self, profile_id: str, full_name: str, address: str
    ) -> Tuple[float, float, float, MatchResult]:
        """
        Match provided data against stored profile embeddings

        Args:
            profile_id: Profile to match against
            full_name: Name to compare
            address: Address to compare

        Returns:
            Tuple of (name_similarity, address_similarity, overall_score, classification)
        """
        # Get stored embeddings
        stored_embeddings = pii_storage.get_embeddings(profile_id)

        if not stored_embeddings:
            logger.warning(f"No embeddings found for profile_id={profile_id}")
            return (0.0, 0.0, 0.0, MatchResult.NO_MATCH)

        # Generate embeddings for input data
        name_embedding = embedding_service.generate_embedding(full_name)
        address_embedding = embedding_service.generate_embedding(address)

        # Calculate similarities
        name_similarity = embedding_service.calculate_similarity(
            name_embedding, stored_embeddings["name"]
        )

        address_similarity = embedding_service.calculate_similarity(
            address_embedding, stored_embeddings["address"]
        )

        # Calculate overall score (weighted average)
        # Name is typically more important than address
        overall_score = (name_similarity * 0.6) + (address_similarity * 0.4)

        # Classify based on thresholds
        classification = self._classify_match(
            name_similarity, address_similarity, overall_score
        )

        logger.info(
            f"Match result for profile_id={profile_id}: "
            f"name={name_similarity:.3f}, address={address_similarity:.3f}, "
            f"overall={overall_score:.3f}, classification={classification.value}"
        )

        return (name_similarity, address_similarity, overall_score, classification)

    def _classify_match(
        self, name_sim: float, address_sim: float, overall: float
    ) -> MatchResult:
        """
        Classify match result based on similarity scores

        Args:
            name_sim: Name similarity score
            address_sim: Address similarity score
            overall: Overall similarity score

        Returns:
            MatchResult classification
        """
        # Strong match: both fields above threshold
        if (
            name_sim >= settings.name_similarity_threshold
            and address_sim >= settings.address_similarity_threshold
            and overall >= settings.overall_match_threshold
        ):
            return MatchResult.MATCH

        # Clear no match: both fields significantly below threshold
        if name_sim < 0.5 and address_sim < 0.5:
            return MatchResult.NO_MATCH

        # Strong name match but weak address (could be moved)
        if name_sim >= settings.name_similarity_threshold and address_sim < 0.6:
            return MatchResult.UNCERTAIN

        # Everything else is uncertain
        return MatchResult.UNCERTAIN


# Global service instance
matcher_service = MatcherService()
