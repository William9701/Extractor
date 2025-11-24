"""
Embedding generation and similarity calculation service
Lightweight version for free tier deployment (no heavy ML models)
"""
from typing import List
import numpy as np
from difflib import SequenceMatcher

from app.utils.logger import logger


class EmbeddingService:
    """Service for generating embeddings and calculating similarity"""

    def __init__(self):
        """Initialize the embedding model"""
        logger.info("Embedding service initialized (lightweight mode)")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate a simple embedding vector for text using character frequencies
        This is a lightweight alternative to sentence-transformers for free tier

        Args:
            text: Input text string

        Returns:
            Embedding vector as list of floats
        """
        if not text:
            return [0.0] * 384

        # Simple embedding: Use character frequency and basic features
        text = text.lower()
        embedding = [0.0] * 384

        # Character frequency features (first 26 for a-z)
        for i, char in enumerate('abcdefghijklmnopqrstuvwxyz'):
            embedding[i] = text.count(char) / (len(text) + 1)

        # Length features
        embedding[26] = len(text) / 100.0
        embedding[27] = len(text.split()) / 20.0

        # First characters
        for i, char in enumerate(text[:10]):
            if i < 10:
                embedding[28 + i] = ord(char) / 255.0

        return embedding

    def calculate_similarity(
        self, embedding1: List[float], embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)

            # Ensure result is in [0, 1] range
            similarity = max(0.0, min(1.0, float(similarity)))

            return similarity

        except Exception as e:
            logger.error(f"Similarity calculation failed: {str(e)}")
            return 0.0

    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings
        Uses both embedding similarity and sequence matching for better accuracy

        Args:
            text1: First text string
            text2: Second text string

        Returns:
            Similarity score between 0 and 1
        """
        if not text1 or not text2:
            return 0.0

        # Method 1: Embedding similarity
        embedding1 = self.generate_embedding(text1)
        embedding2 = self.generate_embedding(text2)
        emb_sim = self.calculate_similarity(embedding1, embedding2)

        # Method 2: Sequence matching (for exact/partial matches)
        seq_sim = SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

        # Combine both methods (weighted average)
        combined = (emb_sim * 0.4) + (seq_sim * 0.6)

        return combined


# Global service instance
embedding_service = EmbeddingService()
