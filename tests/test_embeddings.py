"""
Tests for embedding service
"""
import pytest
from app.services.embeddings import embedding_service


class TestEmbeddingService:
    """Tests for embedding generation and similarity"""

    def test_generate_embedding(self):
        """Test embedding generation"""
        text = "John Doe"
        embedding = embedding_service.generate_embedding(text)

        assert isinstance(embedding, list)
        assert len(embedding) == 384  # all-MiniLM-L6-v2 dimension
        assert all(isinstance(x, float) for x in embedding)

    def test_generate_embedding_empty_string(self):
        """Test embedding for empty string"""
        embedding = embedding_service.generate_embedding("")
        assert len(embedding) == 384
        assert all(x == 0.0 for x in embedding)

    def test_calculate_similarity_identical(self):
        """Test similarity of identical texts"""
        text = "John Doe"
        emb1 = embedding_service.generate_embedding(text)
        emb2 = embedding_service.generate_embedding(text)

        similarity = embedding_service.calculate_similarity(emb1, emb2)

        assert 0.99 <= similarity <= 1.0

    def test_calculate_similarity_similar_texts(self):
        """Test similarity of similar texts"""
        emb1 = embedding_service.generate_embedding("John Doe")
        emb2 = embedding_service.generate_embedding("John David Doe")

        similarity = embedding_service.calculate_similarity(emb1, emb2)

        assert 0.6 <= similarity <= 1.0

    def test_calculate_similarity_different_texts(self):
        """Test similarity of very different texts"""
        emb1 = embedding_service.generate_embedding("John Doe")
        emb2 = embedding_service.generate_embedding("123 Main Street")

        similarity = embedding_service.calculate_similarity(emb1, emb2)

        assert 0.0 <= similarity < 0.5

    def test_calculate_text_similarity(self):
        """Test direct text similarity calculation"""
        similarity = embedding_service.calculate_text_similarity("John Doe", "John Doe")

        assert 0.99 <= similarity <= 1.0
