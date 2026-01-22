---
title: Phase 2 - Backend API Development (File Upload & Gemini Integration)
project: Assignment
date: 2026-01-22
phase: Continuous Execution - Priority 2 (Backend API)
status: EXECUTABLE
---

# Phase 2: Backend API Development

**Objective:** Implement file upload, CSV/XLSX parsing, and Gemini integration  
**Estimated Time:** 4-6 hours  
**Prerequisite:** FastAPI running from Phase 1  

---

## 🎯 Priority Execution Order

**DO NOT SKIP STEPS - Execute in this exact order:**

1. ✅ **Backend Task 2.1:** Create File Validator Service (CSV/XLSX parsing)
2. → **Backend Task 2.2:** Create Upload Endpoint with validation
3. → **Backend Task 2.3:** Test Upload Endpoint locally
4. → **Backend Task 2.4:** Create Gemini Analyzer Service
5. → **Backend Task 2.5:** Create Analysis Endpoint
6. → **Backend Task 2.6:** End-to-end testing

---

# TASK 2.1: Create File Validator Service

**Effort:** 1-2 hours  
**Files to Create/Edit:** `app/services/file_validator.py`

## Step 1: Create File Validator Service

**File:** `app/services/file_validator.py`

```powershell
@"
import logging
import os
import io
from typing import List, Optional
import pandas as pd
import openpyxl
from app.models import SurveyData, SurveyResponse

logger = logging.getLogger(__name__)

class FileValidator:
    """Validates and parses survey files (CSV/XLSX)"""
    
    MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {'.csv', '.xlsx'}
    
    def __init__(self):
        self.logger = logger
    
    def normalize_text(self, text: str) -> str:
        """Normalize survey response text"""
        if not text:
            return ""
        
        text = str(text).strip()
        # Remove extra whitespace
        text = " ".join(text.split())
        # Handle encoding
        text = text.encode('utf-8', errors='ignore').decode('utf-8')
        
        return text
    
    def validate_file_format(self, filename: str) -> str:
        """Check if file format is allowed"""
        ext = os.path.splitext(filename)[1].lower()
        
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported file format: {ext}. Please upload CSV or XLSX.")
        
        return ext
    
    def validate_csv(self, file_content: bytes) -> SurveyData:
        """Parse and validate CSV file"""
        try:
            self.logger.info("Starting CSV parsing")
            
            # Read CSV
            df = pd.read_csv(io.BytesIO(file_content))
            
            self.logger.info(f"CSV loaded: {len(df)} rows, {len(df.columns)} columns")
            
            # Validate headers exist
            if df.empty or len(df.columns) == 0:
                raise ValueError("CSV file has no headers")
            
            # Extract text responses (assume first column)
            responses = []
            for idx, row in df.iterrows():
                # Get first non-null value from row
                text = None
                for val in row:
                    if pd.notna(val):
                        text = self.normalize_text(str(val))
                        if text:
                            break
                
                if text and text.lower() != "nan":
                    responses.append(SurveyResponse(
                        text=text,
                        respondent_id=str(idx)
                    ))
            
            if not responses:
                raise ValueError("CSV file contains no valid response data")
            
            self.logger.info(f"Extracted {len(responses)} responses from CSV")
            
            return SurveyData(
                responses=responses,
                format="csv"
            )
        
        except Exception as e:
            self.logger.error(f"CSV parsing error: {str(e)}")
            raise
    
    def validate_xlsx(self, file_content: bytes) -> SurveyData:
        """Parse and validate XLSX file"""
        try:
            self.logger.info("Starting XLSX parsing")
            
            # Load workbook
            workbook = openpyxl.load_workbook(io.BytesIO(file_content))
            
            # Use first sheet
            sheet = workbook.active
            self.logger.info(f"Using sheet: {sheet.title}")
            
            # Extract all rows
            rows = list(sheet.iter_rows(values_only=True))
            
            if not rows:
                raise ValueError("Excel file is empty")
            
            # Extract responses (skip header row)
            responses = []
            for row_idx, row in enumerate(rows[1:], start=2):
                if row and row[0]:
                    text = self.normalize_text(str(row[0]))
                    
                    if text and text.lower() != "none" and text.lower() != "nan":
                        responses.append(SurveyResponse(
                            text=text,
                            respondent_id=f"row_{row_idx}"
                        ))
            
            if not responses:
                raise ValueError("Excel file contains no valid response data")
            
            self.logger.info(f"Extracted {len(responses)} responses from XLSX")
            
            return SurveyData(responses=responses, format="xlsx")
        
        except Exception as e:
            self.logger.error(f"XLSX parsing error: {str(e)}")
            raise
    
    def validate_file(self, filename: str, file_content: bytes) -> SurveyData:
        """Auto-detect and validate file format"""
        # Validate format
        ext = self.validate_file_format(filename)
        
        # Validate size
        if len(file_content) > self.MAX_FILE_SIZE_BYTES:
            raise ValueError(f"File exceeds {self.MAX_FILE_SIZE_BYTES / (1024*1024):.0f}MB limit")
        
        # Validate not empty
        if not file_content or len(file_content) == 0:
            raise ValueError("File is empty")
        
        # Parse based on format
        if ext == ".csv":
            return self.validate_csv(file_content)
        else:  # .xlsx
            return self.validate_xlsx(file_content)


# Create singleton instance
validator = FileValidator()
"@ | Out-File -Encoding utf8 app\services\file_validator.py
```

## Step 2: Verify File Created

```powershell
# Check the file was created
cat app\services\file_validator.py | head -20

# Verify imports work
python -c "from app.services.file_validator import validator; print('✓ FileValidator imported successfully')"
```

**Expected output:**
```
✓ FileValidator imported successfully
```

---

# TASK 2.2: Create Upload Endpoint with Validation

**Effort:** 1-2 hours  
**Files to Create:** `app/routes.py`

## Step 1: Create Routes File

**File:** `app/routes.py`

```powershell
@"
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
"@ | Out-File -Encoding utf8 app\routes.py
```

## Step 2: Register Routes in main.py

**Edit:** `main.py` - Add this after the CORS middleware section:

```powershell
# Read current main.py
$content = Get-Content main.py -Raw

# Find the insertion point (after CORSMiddleware setup, before try/except for static files)
# Replace this section:
$old = @"
)

try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
"@

$new = @"
)

# Include routes
from app.routes import router
app.include_router(router)

try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
"@

$content = $content -replace [regex]::Escape($old), $new

# Write back
$content | Out-File -Encoding utf8 main.py
```

**Verify:**
```powershell
# Check that routes are imported
grep -n "from app.routes import" main.py
grep -n "app.include_router" main.py
```

**Expected output:**
```
Line 19: from app.routes import router
Line 20: app.include_router(router)
```

---

# TASK 2.3: Test Upload Endpoint

**Effort:** 30 min  
**Test the endpoint locally before proceeding**

## Step 1: Create Test CSV File

```powershell
# Create test data
$testCsv = @"
"Survey Response"
"I absolutely love the story in this game"
"The gameplay is fun but graphics need improvement"
"Excellent narrative, compelling characters"
"Too many bugs, but the core concept is great"
"Best indie game I've played this year"
"Could use more content and longer playtime"
"The art style is beautiful and unique"
"Story pacing is slow but engaging"
"Would definitely recommend to friends"
"Needs better performance optimization"
"@ 

$testCsv | Out-File -Encoding utf8 test_survey.csv
```

## Step 2: Test Upload Endpoint

**Keep FastAPI running in first PowerShell tab. In new tab:**

```powershell
# Test with curl (Windows 10+)
curl -X POST -F "file=@test_survey.csv" http://localhost:8000/upload

# Alternative: Use Python requests (if curl not working)
python -c "
import requests
with open('test_survey.csv', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/upload', files=files)
    print(response.status_code)
    print(response.json())
"
```

**Expected output:**
```json
{
  "status": "success",
  "message": "File validated and ready for analysis",
  "responses_count": 10,
  "format": "csv",
  "survey_data": {
    "responses": [
      {"text": "I absolutely love the story in this game", "respondent_id": "0"},
      ...
    ],
    "format": "csv"
  }
}
```

## Step 3: Test Error Cases

```powershell
# Test 1: Wrong file format
echo "test" | Out-File -Encoding utf8 test.txt
curl -X POST -F "file=@test.txt" http://localhost:8000/upload
# Expected: 415 error, "Unsupported file format"

# Test 2: Empty file
"" | Out-File -Encoding utf8 empty.csv
curl -X POST -F "file=@empty.csv" http://localhost:8000/upload
# Expected: 400 error, "empty"

# Clean up
Remove-Item test.txt, empty.csv
```

**If all tests pass → Continue to Task 2.4**

---

# TASK 2.4: Create Gemini Analyzer Service

**Effort:** 2-3 hours  
**Files to Create:** `app/services/gemini_analyzer.py`

## Step 1: Create Gemini Analyzer Service

**File:** `app/services/gemini_analyzer.py`

```powershell
@"
import logging
import json
import asyncio
import google.generativeai as genai
from typing import Optional
from app.models import (
    PlayerPersona, Demographics, Motivations, PainPoints, SpendingHabits
)
from app.config import settings

logger = logging.getLogger(__name__)

class GeminiAnalyzer:
    """Analyze survey data using Gemini 2.5 API"""
    
    def __init__(self):
        try:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-2.5-pro')
            self.logger = logger
            self.logger.info("Gemini API initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini: {str(e)}")
            raise
    
    def create_analysis_prompt(self, survey_responses: list) -> str:
        """Create a prompt for Gemini to analyze survey data"""
        
        responses_text = "\n".join([f"- {resp}" for resp in survey_responses])
        
        prompt = f"""You are an expert game design analyst specializing in player psychology and experience design.

Analyze the following player survey responses and create a detailed player persona.

SURVEY RESPONSES:
{responses_text}

Generate a comprehensive player persona with these EXACT JSON structure (no markdown, pure JSON):

{{
  "archetype_name": "A memorable persona name (e.g., 'The Curious Adventurer')",
  "demographics": {{
    "age_range": "e.g., '24-32'",
    "gaming_frequency": "e.g., '30+ hours per week'",
    "preferred_genres": ["list", "of", "genres"],
    "primary_platform": "e.g., 'PC'"
  }},
  "motivations": {{
    "primary_driver": "Main reason they play",
    "engagement_factors": ["what", "keeps", "them", "engaged"],
    "psychological_profile": "Description of psychological drivers"
  }},
  "pain_points": {{
    "frustrations": ["what", "frustrates", "them"],
    "what_they_hate": "Main dislike or pain point"
  }},
  "spending_habits": {{
    "in_game_purchase_likelihood": "e.g., 'Moderate - would pay for story DLC'",
    "monetization_preference": "e.g., 'Battle Pass or Story DLC'",
    "price_sensitivity": "e.g., 'Willing to pay 20+ for significant content'"
  }}
}}

IMPORTANT:
- Return ONLY valid JSON, no markdown or extra text
- Base all information on the actual survey responses
- Be specific and actionable in descriptions
- Focus on game player psychology, not generic personas
- All fields must be populated based on the survey data
"""
        return prompt
    
    async def analyze_survey(self, survey_responses: list, game_title: Optional[str] = None) -> PlayerPersona:
        """
        Analyze survey responses and generate player persona
        
        Args:
            survey_responses: List of survey response texts
            game_title: Optional game title for context
            
        Returns:
            PlayerPersona object with analysis results
        """
        try:
            self.logger.info(f"Starting analysis of {len(survey_responses)} responses")
            
            # Create prompt
            prompt = self.create_analysis_prompt(survey_responses)
            
            # Call Gemini API synchronously (convert to async later if needed)
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2048,
                )
            )
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            response_text = response_text.strip()
            
            self.logger.info(f"Gemini response received, parsing JSON")
            
            # Parse JSON
            persona_data = json.loads(response_text)
            
            # Validate and create PersonaResponse model
            persona = PlayerPersona(
                archetype_name=persona_data["archetype_name"],
                demographics=Demographics(**persona_data["demographics"]),
                motivations=Motivations(**persona_data["motivations"]),
                pain_points=PainPoints(**persona_data["pain_points"]),
                spending_habits=SpendingHabits(**persona_data["spending_habits"])
            )
            
            self.logger.info(f"✓ Persona generated successfully: {persona.archetype_name}")
            
            return persona
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse Gemini JSON response: {str(e)}")
            raise ValueError(f"Failed to parse API response as JSON")
        
        except Exception as e:
            self.logger.error(f"Gemini analysis error: {str(e)}")
            raise


# Create singleton instance
analyzer = GeminiAnalyzer()
"@ | Out-File -Encoding utf8 app\services\gemini_analyzer.py
```

## Step 2: Verify Gemini Service

```powershell
# Test Gemini initialization
python -c "
from app.services.gemini_analyzer import analyzer
print('✓ Gemini analyzer initialized')
print(f'✓ Model: {analyzer.model.model_name}')
"
```

**Expected output:**
```
✓ Gemini analyzer initialized
✓ Model: models/gemini-2.5-pro
```

**If you get an auth error, check your .env has correct GEMINI_API_KEY**

---

# TASK 2.5: Create Analysis Endpoint

**Effort:** 1-2 hours  
**Edit:** `app/routes.py`

## Step 1: Update routes.py with Analysis Endpoint

**Add this to the end of `app/routes.py` (before the closing quotes):**

```powershell
# First, read current routes.py
$routesFile = Get-Content app\routes.py -Raw

# Find insertion point - we'll add the new endpoint before the last section
$insertBefore = @"
            "message": "An unexpected error occurred during file processing"
            }
        )
"@

# New analysis endpoint code
$analysisEndpoint = @"
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
"@

# Replace
$routesFile = $routesFile -replace [regex]::Escape($insertBefore), $analysisEndpoint

# Write back
$routesFile | Out-File -Encoding utf8 app\routes.py
```

**Verify it was added:**
```powershell
grep -n "@router.post" app\routes.py
# Should show both /upload and /analyze endpoints
```

---

# TASK 2.6: End-to-End Testing

**Effort:** 1 hour  
**Test both endpoints together**

## Step 1: Restart FastAPI Server

```powershell
# In the tab with running server, press CTRL+C to stop
CTRL+C

# Restart
python main.py
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

## Step 2: Check API Docs

**Open in browser:**
```
http://localhost:8000/api/docs
```

**Verify you see:**
- ✅ GET /health
- ✅ GET /
- ✅ POST /upload
- ✅ POST /analyze

## Step 3: Test Upload Endpoint

**In new PowerShell tab:**

```powershell
# Use existing test_survey.csv
curl -X POST -F "file=@test_survey.csv" http://localhost:8000/upload
```

**Expected:** Status 200 with survey data extracted

## Step 4: Test Analysis Endpoint (Complete Flow)

```powershell
# Call /analyze endpoint
curl -X POST -F "file=@test_survey.csv" http://localhost:8000/analyze
```

**Expected output:** Full persona JSON with:
- archetype_name
- demographics
- motivations
- pain_points
- spending_habits

**Example response:**
```json
{
  "status": "success",
  "message": "Player persona generated successfully",
  "persona": {
    "archetype_name": "The Story-Driven Explorer",
    "demographics": {
      "age_range": "20-35",
      "gaming_frequency": "20-30 hours per week",
      "preferred_genres": ["RPG", "Adventure", "Narrative-driven"],
      "primary_platform": "PC"
    },
    "motivations": {
      "primary_driver": "Deep narrative and character development",
      ...
    }
    ...
  }
}
```

---

# ✅ CHECKPOINT: Backend Phase 2 Complete!

**Verify you have:**
- ✅ File validator service parsing CSV/XLSX
- ✅ Upload endpoint returning validated survey data
- ✅ Gemini analyzer initialized with API key
- ✅ Analysis endpoint generating personas
- ✅ Both endpoints tested and working
- ✅ No console errors

---

# 🚀 NEXT: Frontend Phase 3

**Ready for:**
1. Jinja2 templates (HTML upload form)
2. Tailwind CSS styling (professional UI)
3. Copy to clipboard functionality
4. Error display modal

**Message me when:**
- Upload endpoint working ✓
- Analysis endpoint generating personas ✓
- FastAPI running without errors ✓

**Then I'll provide Phase 3 (Frontend) immediately!**

---

**Status:** Phase 2 Ready for Execution  
**Next Phase:** Frontend Integration (Starts after this is complete)
