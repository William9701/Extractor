"""
Document PII extraction service using AI (Google Gemini or OpenAI)
"""
import base64
from typing import Tuple
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
    """Service for extracting PII from documents using AI"""

    def __init__(self):
        """Initialize AI client based on available API keys"""
        self.provider = None
        self.client = None

        # Try Gemini first (has free tier)
        if settings.google_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.google_api_key)
                self.client = genai.GenerativeModel('gemini-2.5-flash')
                self.provider = "gemini"
                logger.info("Initialized Gemini AI for extraction (FREE tier)")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {str(e)}")

        # Fallback to OpenAI
        elif settings.openai_api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=settings.openai_api_key)
                self.provider = "openai"
                logger.info("Initialized OpenAI for extraction")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {str(e)}")

        if not self.provider:
            logger.warning("No AI provider configured - using mock data")

    def extract_from_image(
        self, image_data: bytes, document_type: str
    ) -> ExtractedPII:
        """
        Extract PII from image using AI

        Args:
            image_data: Image file bytes
            document_type: Type of document being processed

        Returns:
            ExtractedPII object with normalized fields
        """
        if not self.provider:
            logger.warning("Using mock extraction - no API key configured")
            return self._mock_extraction()

        try:
            if self.provider == "gemini":
                return self._extract_with_gemini(image_data, document_type)
            elif self.provider == "openai":
                return self._extract_with_openai(image_data, document_type)
            else:
                return self._mock_extraction()
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            logger.warning("Falling back to mock data")
            return self._mock_extraction()

    def _extract_with_gemini(
        self, image_data: bytes, document_type: str
    ) -> ExtractedPII:
        """Extract using Google Gemini Vision"""
        from PIL import Image
        import io

        # Convert bytes to PIL Image for Gemini
        image = Image.open(io.BytesIO(image_data))

        # Create extraction prompt
        prompt = self._create_extraction_prompt(document_type)

        # Call Gemini
        logger.info("Calling Google Gemini for extraction...")
        response = self.client.generate_content([prompt, image])

        # Parse response
        content = response.text
        logger.info(f"Received Gemini response: {content[:100]}...")

        return self._parse_extraction_response(content)

    def _extract_with_openai(
        self, image_data: bytes, document_type: str
    ) -> ExtractedPII:
        """Extract using OpenAI GPT-4 Vision"""
        # Convert image to base64
        base64_image = base64.b64encode(image_data).decode("utf-8")

        # Create prompt
        prompt = self._create_extraction_prompt(document_type)

        # Call OpenAI
        logger.info("Calling OpenAI GPT-4 Vision for extraction...")
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

        content = response.choices[0].message.content
        logger.info("Received OpenAI response")

        return self._parse_extraction_response(content)

    def _create_extraction_prompt(self, document_type: str) -> str:
        """Create extraction prompt for AI"""
        return f"""
You are a document data extraction AI. Extract the following fields from this {document_type} document.

IMPORTANT: Look carefully at the document and extract EXACTLY what you see.

Extract these fields and return ONLY a valid JSON object with this exact structure:

{{
  "full_name": {{"value": "extracted name", "confidence": 0.95}},
  "date_of_birth": {{"value": "extracted dob", "confidence": 0.90}},
  "address": {{"value": "extracted address", "confidence": 0.85}},
  "id_number": {{"value": "extracted id number", "confidence": 0.95}},
  "expiry_date": {{"value": "extracted expiry date", "confidence": 0.90}}
}}

Rules:
- Extract EXACTLY what you see in the document
- confidence should be a number between 0 and 1
- If a field is not found, set value to null and confidence to 0.0
- Return ONLY the JSON object, no additional text before or after
- For dates, include them in any readable format (we'll normalize later)
- For names, include full name as shown on document
- For address, include complete address as shown
- For ID number, include the license/document number
"""

    def _parse_extraction_response(self, response: str) -> ExtractedPII:
        """
        Parse AI response and create ExtractedPII object

        Args:
            response: JSON string from AI

        Returns:
            ExtractedPII with normalized fields
        """
        try:
            # Clean response - remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]

            # Extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start == -1 or json_end == 0:
                logger.error("No JSON found in response")
                return self._mock_extraction()

            json_str = response[json_start:json_end]
            data = json.loads(json_str)

            # Normalize fields
            full_name_val = normalize_name(data.get("full_name", {}).get("value"))
            dob_val = normalize_date(data.get("date_of_birth", {}).get("value"))
            address_val = normalize_address(data.get("address", {}).get("value"))
            id_num_val = normalize_id_number(data.get("id_number", {}).get("value"))
            expiry_val = normalize_date(data.get("expiry_date", {}).get("value"))

            return ExtractedPII(
                full_name=ExtractedField(
                    value=full_name_val,
                    confidence=data.get("full_name", {}).get("confidence", 0.0)
                ),
                date_of_birth=ExtractedField(
                    value=dob_val,
                    confidence=data.get("date_of_birth", {}).get("confidence", 0.0)
                ),
                address=ExtractedField(
                    value=address_val,
                    confidence=data.get("address", {}).get("confidence", 0.0)
                ),
                id_number=ExtractedField(
                    value=id_num_val,
                    confidence=data.get("id_number", {}).get("confidence", 0.0)
                ),
                expiry_date=ExtractedField(
                    value=expiry_val,
                    confidence=data.get("expiry_date", {}).get("confidence", 0.0)
                ),
            )

        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            logger.error(f"Failed to parse extraction response: {str(e)}")
            logger.error(f"Response was: {response[:200]}")
            return self._mock_extraction()

    def _mock_extraction(self) -> ExtractedPII:
        """Return mock extraction data for testing without API key"""
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
