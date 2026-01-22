import logging
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from app.models import UploadResponse, ErrorResponse, SurveyData
from app.services.file_validator import validator

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload")
async def upload_survey(file: UploadFile = File(...)):
    """
    Upload and validate survey file (CSV or XLSX)
    
    Returns:
        - Success (200): Survey data extracted and validated
        - Error (400): Validation error (format, size, empty)
        - Error (415): Unsupported file format
        - Error (413): File too large
        - Error (500): Server error
    """
    try:
        logger.info(f"Upload request: filename={file.filename}")
        
        # Read file content
        file_content = await file.read()
        logger.info(f"File size: {len(file_content) / (1024*1024):.2f}MB")
        
        # Validate and parse file
        survey_data = validator.validate_file(file.filename, file_content)
        
        logger.info(f"File validated successfully. Responses: {len(survey_data.responses)}")
        
        # Success response
        return {
            "status": "success",
            "message": "File validated and ready for analysis",
            "responses_count": len(survey_data.responses),
            "format": survey_data.format,
            "survey_data": survey_data.dict()
        }
    
    except ValueError as e:
        error_msg = str(e)
        logger.warning(f"Validation error: {error_msg}")
        
        # Determine error type and HTTP status
        if "Unsupported file format" in error_msg:
            status_code = 415
            error_type = "unsupported_format"
        elif "exceeds" in error_msg and "MB" in error_msg:
            status_code = 413
            error_type = "file_too_large"
        elif "empty" in error_msg.lower():
            status_code = 400
            error_type = "empty_file"
        else:
            status_code = 400
            error_type = "validation_error"
        
        return JSONResponse(
            status_code=status_code,
            content={
                "status": "error",
                "error_type": error_type,
                "message": error_msg
            }
        )
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error_type": "internal_error",
                "message": "An unexpected error occurred during file processing"
            }
        )


@router.post("/analyze")
async def analyze_survey(file: UploadFile = File(...)):
    """
    Upload survey file and generate AI-powered player persona
    
    Complete workflow:
    1. Validate file (CSV/XLSX)
    2. Extract survey responses
    3. Analyze with Gemini 2.5 API
    4. Return structured persona
    
    Returns:
        - Success (200): Player persona generated
        - Error (400-500): See error details
    """
    try:
        from app.services.gemini_analyzer import analyzer
        
        logger.info(f"Analysis request: {file.filename}")
        
        # Step 1: Read and validate file
        file_content = await file.read()
        survey_data = validator.validate_file(file.filename, file_content)
        
        logger.info(f"File validated. Starting Gemini analysis...")
        
        # Step 2: Extract response texts
        response_texts = [resp.text for resp in survey_data.responses]
        
        # Step 3: Analyze with Gemini
        persona = await analyzer.analyze_survey(response_texts)
        
        logger.info(f"✓ Analysis complete: {persona.archetype_name}")
        
        # Step 4: Return response
        return {
            "status": "success",
            "message": "Player persona generated successfully",
            "persona": persona.dict()
        }
    
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        
        if "Unsupported file format" in str(e):
            return JSONResponse(status_code=415, content={
                "status": "error",
                "error_type": "unsupported_format",
                "message": str(e)
            })
        elif "exceeds" in str(e):
            return JSONResponse(status_code=413, content={
                "status": "error",
                "error_type": "file_too_large",
                "message": str(e)
            })
        else:
            return JSONResponse(status_code=400, content={
                "status": "error",
                "error_type": "validation_error",
                "message": str(e)
            })
    
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        
        return JSONResponse(status_code=500, content={
            "status": "error",
            "error_type": "analysis_error",
            "message": "Failed to generate persona. Please try again."
        })
