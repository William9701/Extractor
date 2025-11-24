"""
Document PII extraction service using LLM
"""
import base64
from typing import Tuple
from openai import OpenAI
from PIL import Image
import io
import json

from app.config import settings
from app.models.schemas import ExtractedPII, ExtractedField
from app.utils.logger import logger
from app.utils.normalizer import (
    normalize_date,
    normalize_name,
    normalize_address,
    normalize_id_number,
)


class ExtractionService:
    """Service for extracting PII from documents using LLM"""

    def __init__(self):
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not configured")
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.openai_api_key)

    def extract_from_image(
        self, image_data: bytes, document_type: str
    ) -> ExtractedPII:
        """
        Extract PII from image using GPT-4 Vision

        Args:
            image_data: Image file bytes
            document_type: Type of document being processed

        Returns:
            ExtractedPII object with normalized fields
        """
        if not self.client:
            # Return mock data if API key not configured
            logger.warning("Using mock extraction - no API key configured")
            return self._mock_extraction()

        # Convert image to base64
        base64_image = base64.b64encode(image_data).decode("utf-8")

        # Create prompt for extraction
        prompt = self._create_extraction_prompt(document_type)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=1000,
            )

            # Parse the response
            content = response.choices[0].message.content
            logger.info("Received extraction response from LLM")

            return self._parse_extraction_response(content)

        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            raise Exception(f"Failed to extract PII: {str(e)}")

    def _create_extraction_prompt(self, document_type: str) -> str:
        """Create extraction prompt based on document type"""
        return f"""
You are a document data extraction AI. Extract the following fields from this {document_type} document.

Extract these fields and return ONLY a valid JSON object with this exact structure:

{{
  "full_name": {{"value": "extracted name", "confidence": 0.95}},
  "date_of_birth": {{"value": "extracted dob", "confidence": 0.90}},
  "address": {{"value": "extracted address", "confidence": 0.85}},
  "id_number": {{"value": "extracted id number", "confidence": 0.95}},
  "expiry_date": {{"value": "extracted expiry date", "confidence": 0.90}}
}}

Rules:
- confidence should be a number between 0 and 1
- If a field is not found, set value to null and confidence to 0.0
- Return ONLY the JSON object, no additional text
- For dates, try to include them in a readable format
"""

    def _parse_extraction_response(self, response: str) -> ExtractedPII:
        """
        Parse LLM response and create ExtractedPII object

        Args:
            response: JSON string from LLM

        Returns:
            ExtractedPII with normalized fields
        """
        try:
            # Extract JSON from response (handle cases where LLM adds text)
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            json_str = response[json_start:json_end]

            data = json.loads(json_str)

            # Normalize fields
            full_name_val = normalize_name(data["full_name"]["value"])
            dob_val = normalize_date(data["date_of_birth"]["value"])
            address_val = normalize_address(data["address"]["value"])
            id_num_val = normalize_id_number(data["id_number"]["value"])
            expiry_val = normalize_date(data["expiry_date"]["value"])

            return ExtractedPII(
                full_name=ExtractedField(
                    value=full_name_val, confidence=data["full_name"]["confidence"]
                ),
                date_of_birth=ExtractedField(
                    value=dob_val, confidence=data["date_of_birth"]["confidence"]
                ),
                address=ExtractedField(
                    value=address_val, confidence=data["address"]["confidence"]
                ),
                id_number=ExtractedField(
                    value=id_num_val, confidence=data["id_number"]["confidence"]
                ),
                expiry_date=ExtractedField(
                    value=expiry_val, confidence=data["expiry_date"]["confidence"]
                ),
            )

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse extraction response: {str(e)}")
            raise Exception(f"Invalid extraction response format: {str(e)}")

    def _mock_extraction(self) -> ExtractedPII:
        """Return mock extraction data for testing"""
        return ExtractedPII(
            full_name=ExtractedField(value="John Doe", confidence=0.95),
            date_of_birth=ExtractedField(value="1990-01-15", confidence=0.90),
            address=ExtractedField(
                value="123 Main Street, San Jose CA 95110", confidence=0.85
            ),
            id_number=ExtractedField(value="DL12345678", confidence=0.95),
            expiry_date=ExtractedField(value="2028-01-15", confidence=0.90),
        )


# Global service instance
extraction_service = ExtractionService()
