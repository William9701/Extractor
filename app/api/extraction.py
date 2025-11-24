"""
API routes for document PII extraction
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from app.models.schemas import ExtractionResponse, DocumentType
from app.services.extractor import extraction_service
from app.services.embeddings import embedding_service
from app.services.storage import pii_storage
from app.utils.logger import logger

router = APIRouter(prefix="/extract", tags=["extraction"])


@router.post("", response_model=ExtractionResponse)
async def extract_pii(
    file: UploadFile = File(...),
    profile_id: str = Form(...),
    document_type: str = Form(...),
) -> ExtractionResponse:
    """
    Extract structured PII from uploaded document

    Args:
        file: PDF or image file
        profile_id: Unique profile identifier
        document_type: Type of document (driver_license, passport, etc.)

    Returns:
        Extracted and normalized PII fields with confidence scores
    """
    try:
        # Validate document type
        try:
            doc_type = DocumentType(document_type)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid document_type: {document_type}"
            )

        # Read file content
        content = await file.read()

        if not content:
            raise HTTPException(status_code=400, detail="Empty file provided")

        logger.info(
            f"Processing extraction request: profile_id={profile_id}, "
            f"document_type={document_type}, file_size={len(content)} bytes"
        )

        # Extract PII
        extracted_pii = extraction_service.extract_from_image(content, document_type)

        # Store PII
        pii_storage.store_pii(profile_id, extracted_pii)

        # Generate and store embeddings
        name_embedding = embedding_service.generate_embedding(
            extracted_pii.full_name.value or ""
        )
        address_embedding = embedding_service.generate_embedding(
            extracted_pii.address.value or ""
        )

        pii_storage.store_embeddings(profile_id, name_embedding, address_embedding)

        # Build response
        response = ExtractionResponse(
            profile_id=profile_id, document_type=document_type, fields=extracted_pii
        )

        logger.info(f"Extraction completed successfully for profile_id={profile_id}")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")
