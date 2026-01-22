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
