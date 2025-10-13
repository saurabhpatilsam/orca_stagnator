"""
FastAPI Server for CSV Upload
==============================
Provides REST API endpoint for uploading tick data to Supabase
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
import os
from pathlib import Path
from upload_tick_data import TickDataUploader, CSVAnalyzer
from loguru import logger

app = FastAPI(title="Supabase CSV Upload API")

# CORS middleware
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*")
if allowed_origins != "*":
    allowed_origins = allowed_origins.split(",")
else:
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Supabase CSV Upload API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/api/upload-tick-data"
        }
    }

@app.post("/api/upload-tick-data")
async def upload_tick_data(
    file: UploadFile = File(None),
    file_path: str = Form(None),
    instrument: str = Form(...),
    has_header: bool = Form(True),
    skip_duplicates: bool = Form(True),
    supabase_target: str = Form("selfhosted")
):
    """
    Upload tick data TXT file to Supabase (self-hosted or cloud)
    
    Args:
        file: Uploaded TXT file (optional if file_path provided)
        file_path: Path to TXT file on server (optional if file provided)
        instrument: ES or NQ
        has_header: Whether TXT file has header row
        skip_duplicates: Whether to skip duplicate rows
        supabase_target: 'selfhosted' or 'cloud' (default: selfhosted)
    
    Returns:
        JSON with upload results
    """
    
    try:
        # Validate instrument
        if instrument not in ['ES', 'NQ']:
            raise HTTPException(status_code=400, detail="Instrument must be ES or NQ")
        
        # Determine file path
        temp_file_path = None
        csv_file_path = None
        
        if file:
            # Save uploaded file to temp location
            temp_file_path = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
            content = await file.read()
            temp_file_path.write(content)
            temp_file_path.close()
            csv_file_path = temp_file_path.name
            logger.info(f"Uploaded file saved to: {csv_file_path}")
            
        elif file_path:
            # Use provided file path
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
            csv_file_path = file_path
            logger.info(f"Using file path: {csv_file_path}")
            
        else:
            raise HTTPException(status_code=400, detail="Either file or file_path must be provided")
        
        # Analyze TXT file
        logger.info("Analyzing TXT file...")
        date_range = CSVAnalyzer.detect_date_range(csv_file_path, has_header=has_header)
        
        if not date_range:
            raise HTTPException(status_code=400, detail="Could not detect date range from file")
        
        # Upload to Supabase (self-hosted or cloud)
        logger.info(f"Starting upload to {supabase_target.upper()} Supabase (instrument={instrument}, skip_duplicates={skip_duplicates})...")
        uploader = TickDataUploader(supabase_target=supabase_target)
        
        result = uploader.upload_csv(
            csv_file=csv_file_path,
            instrument=instrument,
            skip_duplicates=skip_duplicates,
            has_header=has_header
        )
        
        # Clean up temp file
        if temp_file_path:
            try:
                os.unlink(csv_file_path)
            except:
                pass
        
        # Return result
        if result.get('success'):
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Upload completed successfully",
                    "total_rows": result.get('total_rows', 0),
                    "uploaded_rows": result.get('uploaded_rows', 0),
                    "skipped_rows": result.get('skipped_rows', 0),
                    "error_rows": result.get('error_rows', 0),
                    "date_range": {
                        "start": str(date_range[0]),
                        "end": str(date_range[1])
                    }
                }
            )
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Upload failed'))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "csv-upload-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
