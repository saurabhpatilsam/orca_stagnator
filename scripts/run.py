import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    # Set longer timeout for large file uploads (15 minutes)
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        timeout_keep_alive=900,  # 15 minutes
        timeout_graceful_shutdown=30
    )
