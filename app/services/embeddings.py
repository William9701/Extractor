"""
Embedding generation and similarity calculation service
"""
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.utils.logger import logger


class EmbeddingService:
    """Service for generating embeddings and calculating similarity"""

    def __init__(self):
        """Initialize the embedding model"""
        try:
            # Use a lightweight but effective model
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            self.model = None

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text

        Args:
            text: Input text string

        Returns:
            Embedding vector as list of floats
        """
        if not self.model:
            # Return zero vector if model not loaded
            logger.warning("Embedding model not available, returning zero vector")
            return [0.0] * 384

        if not text:
            return [0.0] * 384

        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            return [0.0] * 384

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
            vec1 = np.array(embedding1).reshape(1, -1)
            vec2 = np.array(embedding2).reshape(1, -1)

            # Calculate cosine similarity
            similarity = cosine_similarity(vec1, vec2)[0][0]

            # Ensure result is in [0, 1] range
            similarity = max(0.0, min(1.0, float(similarity)))

            return similarity

        except Exception as e:
            logger.error(f"Similarity calculation failed: {str(e)}")
            return 0.0

    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings

        Args:
            text1: First text string
            text2: Second text string

        Returns:
            Similarity score between 0 and 1
        """
        embedding1 = self.generate_embedding(text1)
        embedding2 = self.generate_embedding(text2)
        return self.calculate_similarity(embedding1, embedding2)


# Global service instance
embedding_service = EmbeddingService()
