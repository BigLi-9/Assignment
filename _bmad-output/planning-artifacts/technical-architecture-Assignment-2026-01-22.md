---
title: Technical Architecture Document
project: Assignment
date: 2026-01-22
author: BigLi
version: 1.0
status: DRAFT
---

# Technical Architecture: Assignment

**Game Satisfaction Survey Analysis Platform**

---

## Executive Summary

**Assignment** is a full-stack Python web application that transforms game satisfaction surveys into vivid player personas using AI-powered semantic analysis. This document defines the technical architecture, technology stack, and implementation approach for MVP v1.0.

**Key Architectural Decisions:**
- Full-stack Python app (FastAPI + Jinja2) for simplicity and maintainability
- Asynchronous FastAPI backend optimized for Gemini 2.5 API integration
- Stateless, in-memory processing (no database for MVP)
- Real-time synchronous analysis with frontend loading spinner
- Cloud-ready containerized deployment architecture
- 5MB file size limit for optimal performance

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         USER BROWSER                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │        Persona Card Frontend (HTML/Tailwind CSS)     │   │
│  │  - File upload input                                 │   │
│  │  - Loading spinner animation                         │   │
│  │  - Visual profile card display                       │   │
│  │  - Copy to clipboard button                          │   │
│  └────────────────────┬─────────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────┘
                          │ HTTP/Form Data
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend Server                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Request Handling (Async)                │   │
│  │  - /upload (POST) - Receive and validate CSV/XLSX   │   │
│  │  - /analyze (POST) - Trigger semantic analysis      │   │
│  │  - /api/docs - Auto-generated API documentation     │   │
│  └───────────────┬──────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         File Validation & Processing Layer           │   │
│  │  - CSV/XLSX format validation                        │   │
│  │  - Row parsing and data cleaning                     │   │
│  │  - Survey text extraction and preparation           │   │
│  │  - 5MB file size enforcement                         │   │
│  └───────────────┬──────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │     Gemini 2.5 API Integration Layer (Async)        │   │
│  │  - API authentication and request formatting         │   │
│  │  - Semantic analysis prompt engineering              │   │
│  │  - Response parsing and error handling               │   │
│  │  - Rate limit and timeout management                 │   │
│  └───────────────┬──────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │       Persona Model & Response Formatting            │   │
│  │  - Parse Gemini response into structured persona     │   │
│  │  - Extract: Demographics, Motivations, Pain Points   │   │
│  │  - Extract: Spending Habits, Archetype Name          │   │
│  │  - Format for frontend display                       │   │
│  └───────────────┬──────────────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────┘
                          │ JSON Response
                          ▼
┌─────────────────────────────────────────────────────────────┐
│               External API: Gemini 2.5                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │     Semantic Analysis & Persona Generation            │   │
│  │  - Natural language understanding                    │   │
│  │  - Player sentiment and motivation extraction        │   │
│  │  - Psychological profiling                           │   │
│  │  - Spending pattern analysis                         │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### 1. **Frontend Layer** (User Interface)
- **Framework:** Jinja2 templates with HTML/Tailwind CSS
- **Functionality:**
  - File upload form with drag-and-drop support
  - Real-time loading spinner during analysis
  - Visual profile card display with structured persona data
  - Copy to clipboard button for persona card content
  - Error message display for validation failures
- **Assets:**
  - Static folder: CSS, JS, images
  - Templates folder: Jinja2 HTML templates
  - Client-side form validation before submission

#### 2. **Request Handling Layer** (FastAPI Endpoints)
- **Technology:** FastAPI with async/await support
- **Endpoints:**
  - `GET /` - Serve main upload page
  - `POST /upload` - Receive CSV/XLSX file
  - `POST /analyze` - Trigger Gemini analysis (async)
  - `GET /api/docs` - Auto-generated Swagger documentation
  - `GET /health` - Health check for monitoring

#### 3. **File Validation Layer**
- **Responsibilities:**
  - Validate file format (CSV or XLSX)
  - Enforce 5MB size limit
  - Parse file and extract survey responses
  - Detect and handle empty rows, missing headers
  - Clean and normalize text data
  - Return structured survey data for API submission
- **Error Handling:**
  - Unsupported format → "Please upload a CSV or XLSX file"
  - File too large → "File exceeds 5MB limit"
  - Missing headers → "Survey file must include header row"
  - No data rows → "Survey file contains no response data"

#### 4. **Gemini 2.5 Integration Layer**
- **Responsibilities:**
  - Format validated survey data into semantic analysis prompt
  - Handle async API calls to Gemini 2.5
  - Manage authentication (API key from environment variables)
  - Parse structured JSON response from Gemini
  - Implement retry logic for transient failures
  - Handle rate limiting gracefully
- **Prompt Engineering:**
  - Provide clear instructions for persona extraction
  - Request output in structured JSON format
  - Include context about game player psychology
  - Examples of desired persona attributes

#### 5. **Persona Model & Response Formatting**
- **Data Model:**
  ```python
  class PlayerPersona(BaseModel):
      archetype_name: str  # AI-generated persona name
      demographics: Demographics
      motivations: Motivations
      pain_points: PainPoints
      spending_habits: SpendingHabits
  ```
- **Responsibilities:**
  - Validate Gemini response structure
  - Extract required persona fields
  - Handle missing or malformed data gracefully
  - Format for JSON API response
  - Prepare for frontend rendering

---

## Technology Stack

### Backend Stack

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| **Framework** | FastAPI | 0.104+ | Async-first, modern, auto-docs, perfect for Gemini API integration |
| **Server** | Uvicorn | 0.24+ | High-performance async ASGI server |
| **File Processing** | openpyxl + pandas | Latest | Robust CSV/XLSX parsing, data cleaning |
| **API Client** | google-generativeai | Latest | Official Google SDK for Gemini API |
| **Validation** | Pydantic | v2 | Type-safe data validation, auto-docs |
| **Environment** | python-dotenv | Latest | Manage API keys securely |

### Frontend Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Templating** | Jinja2 | Built-in with FastAPI, minimal setup |
| **Styling** | Tailwind CSS | Professional UI with minimal custom CSS |
| **HTML** | HTML5 | Standard semantic markup |
| **Client JS** | Vanilla JS | Simple file upload, form handling, clipboard |
| **Icons** | Heroicons/Feather | Free, minimal dependencies |

### Development & Deployment

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Language** | Python 3.11+ | Modern, async support, fast Gemini SDK |
| **Package Manager** | pip + requirements.txt | Simple, standard Python dependency management |
| **Containerization** | Docker | Cloud-ready deployment to Render, Vercel, etc. |
| **Version Control** | Git | Standard VCS with GitHub |
| **Testing** | pytest | Industry standard Python testing |

---

## Project Structure

```
assignment/
├── main.py                          # FastAPI app entry point
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── .gitignore                       # Git ignore rules
├── Dockerfile                       # Docker containerization
├── docker-compose.yml               # Local development Docker setup
│
├── app/
│   ├── __init__.py
│   ├── config.py                    # Configuration and settings
│   ├── models.py                    # Pydantic models (Persona, Survey, etc.)
│   ├── routes.py                    # FastAPI route handlers
│   ├── services/
│   │   ├── __init__.py
│   │   ├── file_validator.py       # CSV/XLSX validation and parsing
│   │   ├── gemini_analyzer.py      # Gemini 2.5 API integration
│   │   └── persona_formatter.py    # Persona data formatting and response prep
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── error_handlers.py       # Centralized error handling
│   │   └── constants.py            # App constants, prompts, etc.
│   └── templates/
│       ├── base.html               # Base template with header/footer
│       ├── index.html              # Main upload page
│       ├── components/
│       │   ├── upload_form.html    # Upload form component
│       │   ├── persona_card.html   # Persona card display component
│       │   └── error_modal.html    # Error message component
│
├── static/
│   ├── css/
│   │   ├── tailwind.css            # Tailwind CSS build output
│   │   └── custom.css              # Custom styles
│   ├── js/
│   │   ├── upload.js               # File upload handling
│   │   ├── api.js                  # API client calls
│   │   └── ui.js                   # UI interactions (copy, spinner, etc.)
│   └── images/
│       └── logo.png                # Assignment logo
│
├── tests/
│   ├── __init__.py
│   ├── test_file_validator.py
│   ├── test_gemini_analyzer.py
│   ├── test_persona_formatter.py
│   └── test_routes.py
│
└── docs/
    ├── API.md                      # API endpoint documentation
    ├── DEPLOYMENT.md               # Deployment instructions
    └── DEVELOPMENT.md              # Development setup guide
```

---

## API Contract

### Endpoint: POST /upload

**Purpose:** Receive and validate survey file, initiate analysis

**Request:**
```http
POST /upload HTTP/1.1
Content-Type: multipart/form-data

file: <CSV or XLSX file, max 5MB>
```

**Response (Success - 200):**
```json
{
  "status": "success",
  "message": "File validated and analysis started",
  "persona": {
    "archetype_name": "The Curious Adventurer",
    "demographics": {
      "age_range": "24-32",
      "gaming_frequency": "30+ hours per week",
      "preferred_genres": ["RPG", "Adventure", "Narrative-driven"],
      "primary_platform": "PC"
    },
    "motivations": {
      "primary_driver": "Story exploration and world discovery",
      "engagement_factors": [
        "Deep narrative elements",
        "Hidden secrets and side quests",
        "Character development"
      ],
      "psychological_profile": "Intrinsically motivated by curiosity and emotional connection"
    },
    "pain_points": {
      "frustrations": [
        "Linear storytelling that doesn't reward exploration",
        "Unclear quest objectives",
        "Performance issues during cinematic scenes"
      ],
      "what_they_hate": "Feeling forced into a predetermined path"
    },
    "spending_habits": {
      "in_game_purchase_likelihood": "Moderate - would pay for story expansions",
      "monetization_preference": "Battle Pass or Story DLC",
      "price_sensitivity": "Willing to pay $20+ for significant content"
    }
  }
}
```

**Response (Validation Error - 400):**
```json
{
  "status": "error",
  "error_type": "validation_error",
  "message": "File exceeds 5MB limit",
  "details": "Please upload a smaller file"
}
```

**Response (API Error - 500):**
```json
{
  "status": "error",
  "error_type": "analysis_error",
  "message": "Failed to analyze survey data",
  "details": "Gemini API temporarily unavailable. Please try again."
}
```

---

### Endpoint: GET /api/docs

**Purpose:** Access auto-generated API documentation

**Response:** Interactive Swagger UI showing all endpoints, models, and schemas

---

## Data Models

### Pydantic Models (Type Safety & Validation)

```python
# Survey & File Data
class SurveyResponse(BaseModel):
    text: str
    respondent_id: Optional[str] = None

class SurveyData(BaseModel):
    responses: List[SurveyResponse]
    game_title: Optional[str] = None
    survey_date: Optional[str] = None

# Persona Components
class Demographics(BaseModel):
    age_range: str
    gaming_frequency: str
    preferred_genres: List[str]
    primary_platform: str

class Motivations(BaseModel):
    primary_driver: str
    engagement_factors: List[str]
    psychological_profile: str

class PainPoints(BaseModel):
    frustrations: List[str]
    what_they_hate: str

class SpendingHabits(BaseModel):
    in_game_purchase_likelihood: str
    monetization_preference: str
    price_sensitivity: str

# Complete Persona
class PlayerPersona(BaseModel):
    archetype_name: str
    demographics: Demographics
    motivations: Motivations
    pain_points: PainPoints
    spending_habits: SpendingHabits

class AnalysisResponse(BaseModel):
    status: str
    message: str
    persona: PlayerPersona
```

---

## Asynchronous Processing Flow

### Real-Time Synchronous Analysis (MVP)

```python
# User uploads file
async def handle_upload(file: UploadFile):
    # 1. Validate file (fast, < 1 second)
    survey_data = await validate_and_parse_file(file)
    
    # 2. Call Gemini API (async, 3-10 seconds)
    gemini_response = await call_gemini_api(survey_data)
    
    # 3. Format response (fast, < 1 second)
    persona = format_persona_response(gemini_response)
    
    # 4. Return to frontend (total: 4-11 seconds)
    return {"status": "success", "persona": persona}
```

**Frontend Behavior:**
- Show loading spinner while analysis runs
- Display persona immediately upon completion
- Show error message if analysis fails
- Spinner text: "Analyzing survey with AI... (3-10 seconds)"

---

## Error Handling Strategy

### File Validation Errors

| Error | Status | Message | Action |
|-------|--------|---------|--------|
| Wrong format | 400 | "Please upload a CSV or XLSX file" | Reject, show form again |
| File too large | 413 | "File exceeds 5MB limit" | Reject, suggest smaller file |
| No headers | 400 | "Survey file must include header row" | Reject, show format requirements |
| No data rows | 400 | "Survey file contains no response data" | Reject, ask for more responses |
| Malformed data | 400 | "Unable to parse file. Check formatting" | Reject, show example format |

### API Errors

| Error | Status | Action |
|-------|--------|--------|
| Gemini API timeout | 504 | Retry up to 2 times, then show error |
| Rate limit hit | 429 | Show: "Temporarily busy. Try again in 30 seconds" |
| Invalid API key | 401 | Log error, show: "Service configuration error" |
| Malformed response | 500 | Log error, show: "Analysis failed. Try different survey data" |

### Error Display (Frontend)

- Modal dialog with error icon and clear message
- "Try Again" button to re-upload file
- Helpful suggestions (e.g., "Survey needs at least 10 responses for accurate analysis")

---

## Security Considerations

### API Key Management
- Store Gemini API key in environment variables (`.env`)
- Never commit `.env` to version control
- Use `.env.example` with placeholder values
- Rotate keys periodically

### File Upload Security
- Enforce file type validation (whitelist CSV, XLSX only)
- Enforce file size limit (5MB)
- Scan for malicious content before processing
- Store uploaded files temporarily in memory, never on disk

### Input Validation
- Use Pydantic for strict data validation
- Sanitize text data before sending to Gemini API
- Rate limit API endpoints if needed

### API Responses
- Don't expose stack traces in error messages
- Generic error messages to users, detailed logs for debugging
- CORS headers configured appropriately

---

## Performance Considerations

### Analysis Speed Targets
- File validation: < 1 second
- Gemini API call: 3-10 seconds (depends on Gemini latency)
- Response formatting: < 1 second
- **Total: 4-11 seconds** (Success metric: 30 seconds)

### Optimization Strategies
- Use async/await for non-blocking I/O
- Minimal dependencies for fast startup
- Efficient CSV/XLSX parsing with pandas
- Cache Tailwind CSS for faster rendering

### Scaling Considerations (Future)
- If demand grows, implement request queuing (Celery + Redis)
- Add persona caching for duplicate surveys
- Implement background job processing

---

## Deployment Architecture

### Local Development (Windows)
```
Windows Machine
  ├── Python 3.11 interpreter
  ├── FastAPI + Uvicorn server (localhost:8000)
  ├── .env file with Gemini API key
  └── Browser (http://localhost:8000)
```

### Cloud Deployment (Future - Render/Vercel)
```
Cloud Platform (Render.com / Vercel)
  ├── Docker container with FastAPI app
  ├── Environment variables (Gemini API key)
  ├── Managed Python runtime
  ├── Auto-scaling on demand
  └── Public HTTPS URL
```

### Docker Setup
```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Development Workflow

### Local Setup
1. Clone repository
2. Create Python virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add Gemini API key
5. Run FastAPI: `uvicorn main:app --reload`
6. Access: `http://localhost:8000`

### Testing
```bash
# Run unit tests
pytest tests/

# Test file validator
pytest tests/test_file_validator.py

# Test Gemini integration
pytest tests/test_gemini_analyzer.py

# Test API endpoints
pytest tests/test_routes.py
```

### Deployment Steps
1. Build Docker image: `docker build -t assignment .`
2. Push to cloud registry (Docker Hub / Google Cloud)
3. Deploy to cloud platform (Render, Vercel, etc.)
4. Set environment variables in cloud platform
5. Verify deployment with health check: `GET /health`

---

## Dependencies & Versions

### Production Dependencies
```
fastapi==0.104.1
uvicorn==0.24.0
python-dotenv==1.0.0
pydantic==2.5.0
google-generativeai==0.3.0
pandas==2.1.0
openpyxl==3.11.0
python-multipart==0.0.6
```

### Development Dependencies
```
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.12.0
flake8==6.1.0
```

---

## Risk & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Gemini API downtime | High | Add retry logic, friendly error messages, future fallback models |
| Large file processing | High | Enforce 5MB limit, test with various file sizes |
| API rate limiting | Medium | Implement exponential backoff, document rate limits |
| Poor persona accuracy | High | Test with diverse game genres, iterate with real users |
| Security breach (API key) | Critical | Use environment variables, rotate keys regularly, audit logs |

---

## Success Metrics (Technical)

- ✅ Persona generation completes within 30 seconds (target: < 12 seconds)
- ✅ 98%+ pipeline success rate (upload → analyze → display)
- ✅ 85%+ accuracy in semantic analysis (validated against manual review)
- ✅ Zero crashes on common file errors
- ✅ All endpoints return appropriate status codes and error messages
- ✅ Responsive UI on desktop and tablet devices
- ✅ FastAPI auto-docs working and complete

---

## Next Steps (Iteration 2 & 3)

### Iteration 2: Backend Development
1. Implement file validator service
2. Implement Gemini 2.5 API integration
3. Implement persona formatter service
4. Write unit tests for all services
5. Test with sample survey datasets

### Iteration 3: Frontend Development
1. Build upload form and file input
2. Build persona card display component
3. Implement copy-to-clipboard functionality
4. Add loading spinner and error handling
5. End-to-end integration testing

### Iteration 4: Polish & Deploy
1. Performance optimization
2. Security audit
3. User testing with alpha users
4. Final refinements based on feedback
5. Deploy to cloud platform

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-22  
**Status:** DRAFT - Ready for Development Team Review
