---
title: Repository Setup & Project Initialization
project: Assignment
date: 2026-01-22
phase: Continuous Execution - Priority 1 (Repository Setup)
status: EXECUTABLE
---

# Repository Setup Guide: Assignment

**Game Satisfaction Survey Analysis Platform**

---

## 🚀 Rapid Execution Mode

**Objective:** Get repository initialized and ready for backend development  
**Estimated Time:** 30-45 minutes  
**Next Phase:** Backend API implementation begins immediately after completion

---

## Quick Reference: Priority Order

This follows strict technical priority:

1. **✅ Repo Setup** (This document - 30-45 min)
2. **→ Backend API** (FastAPI foundation, file upload, CSV/XLSX parsing)
3. **→ Frontend Integration** (Jinja2 templates, UI, copy-to-clipboard)

As soon as you complete Repo Setup, move immediately to Backend API tasks.

---

# Phase 1: Repository Setup (30-45 Minutes)

## Step 1: Create GitHub Repository (5 minutes)

### 1.1 On GitHub Web Interface

**Go to:** https://github.com/new

**Settings:**
- Repository name: `assignment`
- Description: `Game Satisfaction Survey Analysis Platform - AI-Powered Player Persona Generator`
- Visibility: **Public** (unless private preferred)
- Initialize with:
  - ✅ Add a README file
  - ✅ Add .gitignore (choose Python)
  - ✅ Add a license (MIT is fine)

**Click:** Create repository

**Copy:** Repository URL (e.g., `https://github.com/YOUR_USERNAME/assignment.git`)

---

## Step 2: Clone Repository Locally (5 minutes)

### 2.1 Open Terminal/PowerShell

**Windows (PowerShell):**
```powershell
# Navigate to where you want the project
cd C:\Users\78785\Desktop

# Clone the repository
git clone https://github.com/YOUR_USERNAME/assignment.git

# Navigate into project
cd assignment

# Verify clone
git status
```

**Expected output:**
```
On branch main

No commits yet

nothing to commit
```

---

## Step 3: Create Project Structure (5 minutes)

### 3.1 Create Directory Structure

**Windows (PowerShell):**
```powershell
# Create main directories
mkdir app
mkdir app\services
mkdir app\utils
mkdir app\templates
mkdir app\static
mkdir app\static\css
mkdir app\static\js
mkdir tests
mkdir docs

# Create __init__ files
@"
"@ | Out-File -Encoding utf8 app\__init__.py
@"
"@ | Out-File -Encoding utf8 app\services\__init__.py
@"
"@ | Out-File -Encoding utf8 app\utils\__init__.py
@"
"@ | Out-File -Encoding utf8 tests\__init__.py

# Verify structure
tree /F
```

**Expected structure:**
```
assignment/
├── app/
│   ├── __init__.py
│   ├── services/
│   │   └── __init__.py
│   ├── utils/
│   │   └── __init__.py
│   ├── templates/
│   └── static/
│       ├── css/
│       └── js/
├── tests/
│   └── __init__.py
├── docs/
├── .gitignore
├── .env.example
├── requirements.txt
├── main.py
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Step 4: Create Core Files (10 minutes)

### 4.1 Create `requirements.txt`

**Windows (PowerShell):**
```powershell
@"
fastapi==0.104.1
uvicorn==0.24.0
python-dotenv==1.0.0
pydantic==2.5.0
pandas==2.1.0
openpyxl==3.11.0
python-multipart==0.0.6
google-generativeai==0.3.0
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.12.0
flake8==6.1.0
"@ | Out-File -Encoding utf8 requirements.txt
```

**Verify:**
```powershell
cat requirements.txt
```

---

### 4.2 Create `.env.example`

**Windows (PowerShell):**
```powershell
@"
# Gemini API Configuration
GEMINI_API_KEY=your_api_key_here

# File Upload Configuration
MAX_FILE_SIZE_MB=5

# FastAPI Configuration
DEBUG=True
"@ | Out-File -Encoding utf8 .env.example
```

---

### 4.3 Create `main.py` (FastAPI Entry Point)

**Windows (PowerShell):**
```powershell
@"
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Assignment",
    description="Game Satisfaction Survey Analysis Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception as e:
    logger.warning(f"Static files directory not found: {e}")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Assignment API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
"@ | Out-File -Encoding utf8 main.py
```

---

### 4.4 Create `Dockerfile`

**Windows (PowerShell):**
```powershell
@"
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"@ | Out-File -Encoding utf8 Dockerfile
```

---

### 4.5 Create `docker-compose.yml`

**Windows (PowerShell):**
```powershell
@"
version: '3.8'

services:
  assignment:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=`${GEMINI_API_KEY}
      - DEBUG=True
    volumes:
      - .:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"@ | Out-File -Encoding utf8 docker-compose.yml
```

---

### 4.6 Create `app/config.py` (Configuration Management)

**Windows (PowerShell):**
```powershell
@"
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "5"))
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    def __init__(self):
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not configured in .env")

settings = Settings()
"@ | Out-File -Encoding utf8 app\config.py
```

---

### 4.7 Create `app/models.py` (Pydantic Models)

**Windows (PowerShell):**
```powershell
@"
from pydantic import BaseModel
from typing import Optional, List

class SurveyResponse(BaseModel):
    text: str
    respondent_id: Optional[str] = None

class SurveyData(BaseModel):
    responses: List[SurveyResponse]
    format: str = "csv"

class ErrorResponse(BaseModel):
    status: str = "error"
    error_type: str
    message: str
    details: Optional[str] = None

class UploadResponse(BaseModel):
    status: str
    message: str
    responses_count: Optional[int] = None

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
"@ | Out-File -Encoding utf8 app\models.py
```

---

### 4.8 Create `.gitignore` Updates

**Verify/Update existing .gitignore:**
```powershell
@"
# Python
__pycache__/
*.py[cod]
*`$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local
.env.*.local

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db

# Project specific
*.log
temp/
uploads/
"@ | Out-File -Encoding utf8 .gitignore -Append
```

---

## Step 5: Setup Python Virtual Environment (5 minutes)

### 5.1 Create Virtual Environment

**Windows (PowerShell):**
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Verify activation (should show (venv) prefix)
python --version
```

**If activation fails, try:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

---

### 5.2 Install Dependencies

**PowerShell (with venv activated):**
```powershell
pip install --upgrade pip setuptools wheel

pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print(f'FastAPI version: {fastapi.__version__}')"
python -c "import pandas; print(f'Pandas version: {pandas.__version__}')"
python -c "import google.generativeai; print('Gemini SDK installed')"
```

**Expected output:**
```
FastAPI version: 0.104.1
Pandas version: 2.1.0
Gemini SDK installed
```

---

## Step 6: Test FastAPI Server (5 minutes)

### 6.1 Start Server

**PowerShell (with venv activated):**
```powershell
python main.py
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
```

---

### 6.2 Verify Server is Running

**Open new PowerShell tab (keep server running):**
```powershell
# Test health check endpoint
curl http://localhost:8000/health

# Test auto-docs
curl http://localhost:8000/api/docs
```

**Expected:**
- Health check returns: `{"status":"ok","version":"1.0.0"}`
- /api/docs returns HTML docs page

**In browser:** Open http://localhost:8000/api/docs

---

## Step 7: Initial Commit (5 minutes)

### 7.1 Stage and Commit

**PowerShell (stop server with CTRL+C first):**
```powershell
# Check git status
git status

# Add all files
git add .

# Commit
git commit -m "Initial project setup: FastAPI foundation, project structure, dependencies"

# Push to GitHub
git branch -M main
git push -u origin main

# Verify
git log --oneline
```

**Expected:**
```
1 commit: "Initial project setup..."
```

---

## Step 8: Create .env File (Critical for Next Phase)

### 8.1 Create `.env` in Project Root

**Copy from .env.example:**
```powershell
cp .env.example .env
```

**Edit `.env` with your Gemini API key:**
```powershell
notepad .env
```

**Update:**
```
GEMINI_API_KEY=your_actual_gemini_api_key_here
MAX_FILE_SIZE_MB=5
DEBUG=True
```

**How to get Gemini API Key:**
1. Go to: https://ai.google.dev/
2. Click "Get API Key"
3. Create new project
4. Generate API key
5. Copy and paste into .env

**Verify NOT committing .env:**
```powershell
git status  # Should show .env is ignored
```

---

# Checkpoint: Repository Setup Complete ✅

### Verification Checklist

- ✅ GitHub repository created
- ✅ Repository cloned locally
- ✅ Directory structure created
- ✅ All core files created (main.py, requirements.txt, Dockerfile, etc.)
- ✅ Python virtual environment activated
- ✅ All dependencies installed
- ✅ FastAPI server starts without errors
- ✅ Health check endpoint responds
- ✅ FastAPI auto-docs accessible at /api/docs
- ✅ Initial commit pushed to GitHub
- ✅ .env file created with Gemini API key
- ✅ .gitignore properly configured

---

# Quick Reference Commands

**Start Development:**
```powershell
cd assignment
.\venv\Scripts\Activate.ps1
python main.py
```

**Access API Docs:**
```
http://localhost:8000/api/docs
```

**Run Tests:**
```powershell
pytest tests/ -v
```

**Code Formatting:**
```powershell
black app/ tests/ main.py
flake8 app/ tests/ main.py
```

**Docker:**
```powershell
docker build -t assignment .
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key assignment
```

---

# Next Phase: Backend API Development

✅ **REPOSITORY SETUP COMPLETE** → Ready for Backend API

## Immediate Next Tasks (Start NOW):

### Backend Priority 1: File Upload Endpoint
1. Create `app/routes.py` with POST /upload endpoint
2. Implement file size validation (5MB limit)
3. Implement file format validation (CSV/XLSX only)
4. Test with Postman/curl

### Backend Priority 2: CSV/XLSX Parsing
1. Create `app/services/file_validator.py`
2. Implement CSV parser using pandas
3. Implement XLSX parser using openpyxl
4. Add text normalization and error handling

### Backend Priority 3: Gemini Integration
1. Create `app/services/gemini_analyzer.py`
2. Implement Gemini API calls
3. Parse persona response
4. Create analysis endpoint

---

**Repository Setup Document Version:** 1.0  
**Status:** READY FOR EXECUTION  
**Next Phase:** Backend API (Start immediately after setup)

---

## 🎯 You are now ready to:

1. **Clone this repo to your local machine** (5 min)
2. **Setup Python environment** (5 min)  
3. **Start FastAPI server** (2 min)
4. **Begin backend API development** (immediately after)

**Estimated Total:** 30-45 minutes from zero to "FastAPI running locally"

**Then:** Jump directly into Backend API tasks without waiting.
