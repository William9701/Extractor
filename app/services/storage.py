"""
In-memory storage for PII data and embeddings
"""
from typing import Dict, Optional, List
import threading
from app.models.schemas import ExtractedPII
from app.utils.logger import logger


class PIIStorage:
    """Thread-safe in-memory storage for PII and embeddings"""

    def __init__(self):
        self._data: Dict[str, ExtractedPII] = {}
        self._embeddings: Dict[str, Dict[str, List[float]]] = {}
        self._lock = threading.Lock()

    def store_pii(self, profile_id: str, pii: ExtractedPII) -> None:
        """
        Store PII data for a profile

        Args:
            profile_id: Unique profile identifier
            pii: Extracted PII data
        """
        with self._lock:
            self._data[profile_id] = pii
            logger.info(f"Stored PII for profile_id={profile_id}")

    def get_pii(self, profile_id: str) -> Optional[ExtractedPII]:
        """
        Retrieve PII data for a profile

        Args:
            profile_id: Unique profile identifier

        Returns:
            ExtractedPII or None if not found
        """
        with self._lock:
            return self._data.get(profile_id)

    def store_embeddings(
        self, profile_id: str, name_embedding: List[float], address_embedding: List[float]
    ) -> None:
        """
        Store embeddings for a profile

        Args:
            profile_id: Unique profile identifier
            name_embedding: Embedding vector for full_name
            address_embedding: Embedding vector for address
        """
        with self._lock:
            self._embeddings[profile_id] = {
                "name": name_embedding,
                "address": address_embedding,
            }
            logger.info(f"Stored embeddings for profile_id={profile_id}")

    def get_embeddings(self, profile_id: str) -> Optional[Dict[str, List[float]]]:
        """
        Retrieve embeddings for a profile

        Args:
            profile_id: Unique profile identifier

        Returns:
            Dict with 'name' and 'address' embeddings or None
        """
        with self._lock:
            return self._embeddings.get(profile_id)

    def get_all_embeddings(self) -> Dict[str, Dict[str, List[float]]]:
        """
        Get all stored embeddings for search functionality

        Returns:
            Dict mapping profile_id to embeddings
        """
        with self._lock:
            return self._embeddings.copy()

    def get_all_profiles(self) -> List[str]:
        """
        Get all stored profile IDs

        Returns:
            List of profile IDs
        """
        with self._lock:
            return list(self._data.keys())


# Global storage instance
pii_storage = PIIStorage()
