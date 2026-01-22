---
title: Quick Start - Copy-Paste Commands
project: Assignment
date: 2026-01-22
phase: EXECUTION - Repository Setup
---

# 🚀 QUICK START: Copy-Paste Commands

**Time:** 30-45 minutes  
**Platform:** Windows PowerShell  
**Goal:** Repository initialized → FastAPI running locally

---

## ⚠️ IMPORTANT - Before You Start

1. **Create GitHub Account** (if needed): https://github.com
2. **Get Gemini API Key:**
   - Go to: https://ai.google.dev/
   - Click "Get API Key"
   - Generate API key and **COPY IT** (you'll need it in Step 5)

---

# EXECUTION SEQUENCE

## STEP 1: Create GitHub Repository (Do This in Browser)

**Go to:** https://github.com/new

**Fill in:**
- Repository name: `assignment`
- Description: `Game Satisfaction Survey Analysis Platform`
- Visibility: **Public**
- ✅ Check: "Add a README file"
- ✅ Check: "Add .gitignore" (Python)
- ✅ Check: "Add a license" (MIT)

**Click:** "Create repository"

**COPY the URL** that appears (looks like: `https://github.com/YOUR_USERNAME/assignment.git`)

---

## STEP 2: Clone & Setup (PowerShell Commands)

**Open PowerShell and run these commands:**

```powershell
# Navigate to Desktop
cd C:\Users\78785\Desktop

# REPLACE YOUR_USERNAME with your actual GitHub username
# REPLACE https://github.com/YOUR_USERNAME/assignment.git with your repo URL
git clone https://github.com/YOUR_USERNAME/assignment.git

# Enter project directory
cd assignment

# Verify you're in the right place
pwd  # Should show: C:\Users\78785\Desktop\assignment
```

**Expected output:**
```
Cloning into 'assignment'...
warning: You appear to have cloned an empty repository.
```

---

## STEP 3: Create Project Structure

**Copy and run this entire block:**

```powershell
# Create directories
mkdir app\services
mkdir app\utils
mkdir app\templates
mkdir app\static\css
mkdir app\static\js
mkdir tests
mkdir docs

# Create __init__ files
"" | Out-File app\__init__.py
"" | Out-File app\services\__init__.py
"" | Out-File app\utils\__init__.py
"" | Out-File tests\__init__.py

# Verify structure
tree /F
```

**Expected output:** Full directory tree showing all folders

---

## STEP 4: Create Core Files

### 4A: Create requirements.txt

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

### 4B: Create .env.example

```powershell
@"
GEMINI_API_KEY=your_api_key_here
MAX_FILE_SIZE_MB=5
DEBUG=True
"@ | Out-File -Encoding utf8 .env.example
```

### 4C: Create main.py

```powershell
@"
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Assignment",
    description="Game Satisfaction Survey Analysis Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception as e:
    logger.warning(f"Static files directory not found: {e}")

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}

@app.get("/")
async def root():
    return {"message": "Welcome to Assignment API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
"@ | Out-File -Encoding utf8 main.py
```

### 4D: Create Dockerfile

```powershell
@"
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"@ | Out-File -Encoding utf8 Dockerfile
```

### 4E: Create docker-compose.yml

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

### 4F: Create app/config.py

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

### 4G: Create app/models.py

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

## STEP 5: Setup Python Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If activation fails, run this first:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Verify activation (should show (venv) prefix in your prompt)
python --version

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install all dependencies
pip install -r requirements.txt

# Verify key packages
python -c "import fastapi; print(f'✓ FastAPI: {fastapi.__version__}')"
python -c "import pandas; print(f'✓ Pandas installed')"
python -c "import google.generativeai; print(f'✓ Gemini SDK installed')"
```

**Expected output:**
```
✓ FastAPI: 0.104.1
✓ Pandas installed
✓ Gemini SDK installed
```

---

## STEP 6: Create .env File with Your API Key

```powershell
# Copy template
cp .env.example .env

# Open .env in Notepad
notepad .env
```

**In Notepad:**
1. Replace `your_api_key_here` with your **actual Gemini API key** (from Step 1)
2. Save (Ctrl+S)
3. Close

**Example (CHANGE THE KEY):**
```
GEMINI_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxxx
MAX_FILE_SIZE_MB=5
DEBUG=True
```

---

## STEP 7: Test FastAPI Server

**KEEP VENV ACTIVATED, then run:**

```powershell
# Start the server
python main.py
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**✓ LEAVE THIS RUNNING**

---

## STEP 8: Verify Server (New PowerShell Tab)

**Open NEW PowerShell tab (keep server running in first tab):**

```powershell
# Test health check
curl http://localhost:8000/health

# Test root endpoint
curl http://localhost:8000/
```

**Expected output:**
```
{"status":"ok","version":"1.0.0"}
{"message":"Welcome to Assignment API"}
```

**In Browser:** Open http://localhost:8000/api/docs

You should see FastAPI Swagger UI with auto-generated documentation.

---

## STEP 9: Commit to GitHub

**In the new PowerShell tab (NOT the one running the server):**

```powershell
# Stage all files
git add .

# Commit
git commit -m "Initial project setup: FastAPI foundation, project structure"

# Push to GitHub
git push -u origin main

# Verify
git log --oneline
```

**Expected output:**
```
main 1234567 Initial project setup: FastAPI foundation, project structure
```

---

# ✅ CHECKPOINT: Repository Setup Complete!

**Verify you have:**
- ✅ GitHub repo created and cloned
- ✅ Project structure in place
- ✅ All files created (main.py, requirements.txt, etc.)
- ✅ Python venv activated
- ✅ All dependencies installed
- ✅ FastAPI server running on http://localhost:8000
- ✅ Health check responding
- ✅ Auto-docs at http://localhost:8000/api/docs
- ✅ Initial commit pushed to GitHub
- ✅ .env file with Gemini API key

---

# 🚀 NEXT: Backend API Development

**KEEP FASTAPI SERVER RUNNING** in first tab.

In your new PowerShell tab, you're ready for Backend Phase.

**Message me when:**
1. Server is running
2. Health check works
3. You see the Swagger UI at /api/docs

**Then I'll provide Backend API Phase 2 tasks immediately.**

---

## Quick Reference (Keep This Handy)

**Activate venv every time you start:**
```powershell
cd C:\Users\78785\Desktop\assignment
.\venv\Scripts\Activate.ps1
```

**Start server:**
```powershell
python main.py
```

**Stop server:**
```powershell
CTRL+C
```

**View API docs:**
```
http://localhost:8000/api/docs
```

---

**Status:** READY FOR EXECUTION  
**Next Phase:** Backend API (starts immediately after repo setup)
