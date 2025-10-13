"""
FastAPI Server for CSV Upload
==============================
Provides REST API endpoint for uploading tick data to Supabase with real-time progress
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
import tempfile
import os
from upload_tick_data import TickDataUploader, CSVAnalyzer
from loguru import logger
import concurrent.futures

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
    Upload tick data with real-time batch progress streaming
    """
    
    async def progress_stream():
        """Generator for streaming progress updates"""
        progress_queue = []
        
        def progress_callback(data):
            """Callback to capture progress updates"""
            progress_queue.append(data)
        
        try:
            # Validate instrument
            if instrument not in ['ES', 'NQ']:
                yield f"data: {json.dumps({'error': 'Invalid instrument'})}\n\n"
                return
            
            # Handle file upload
            temp_file_path = None
            if file:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
                temp_file_path = temp_file.name
                content = await file.read()
                temp_file.write(content)
                temp_file.close()
                csv_file_path = temp_file_path
            elif file_path:
                csv_file_path = file_path
            else:
                yield f"data: {json.dumps({'error': 'No file provided'})}\n\n"
                return
            
            # Send initial status
            yield f"data: {json.dumps({'status': 'started', 'message': 'Upload started'})}\n\n"
            await asyncio.sleep(0.1)
            
            # Analyze file
            date_range = CSVAnalyzer.detect_date_range(csv_file_path, has_header=has_header)
            if not date_range:
                yield f"data: {json.dumps({'error': 'Could not detect date range'})}\n\n"
                return
            
            # Start upload with progress callback
            uploader = TickDataUploader(supabase_target=supabase_target)
            
            # Run upload in thread pool
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    uploader.upload_csv,
                    csv_file=csv_file_path,
                    instrument=instrument,
                    skip_duplicates=skip_duplicates,
                    has_header=has_header,
                    progress_callback=progress_callback
                )
                
                # Stream progress updates while upload runs
                while not future.done():
                    if progress_queue:
                        update = progress_queue.pop(0)
                        yield f"data: {json.dumps(update)}\n\n"
                    await asyncio.sleep(0.5)
                
                # Send any remaining progress updates
                while progress_queue:
                    update = progress_queue.pop(0)
                    yield f"data: {json.dumps(update)}\n\n"
                
                # Get final result
                result = future.result()
                
                # Clean up temp file
                if temp_file_path:
                    try:
                        os.unlink(csv_file_path)
                    except:
                        pass
                
                # Send completion
                if result.get('success'):
                    completion_data = {
                        'status': 'completed',
                        'success': True,
                        'total_rows': result.get('total_rows', 0),
                        'uploaded_rows': result.get('uploaded_rows', 0),
                        'skipped_rows': result.get('skipped_rows', 0),
                        'table': result.get('table', ''),
                        'duration': result.get('duration', ''),
                        'date_range': {
                            'start': str(date_range[0]),
                            'end': str(date_range[1])
                        }
                    }
                    yield f"data: {json.dumps(completion_data)}\n\n"
                else:
                    yield f"data: {json.dumps({'status': 'error', 'error': result.get('error', 'Upload failed')})}\n\n"
        
        except Exception as e:
            logger.error(f"Upload error: {str(e)}")
            yield f"data: {json.dumps({'status': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        progress_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "csv-upload-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
