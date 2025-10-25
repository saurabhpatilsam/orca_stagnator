from app.utils.logging_setup import logger
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
from datetime import datetime
import json

# Import routers
from app.api.v1.trading_api_router import trading_router, hedge_router
from app.api.v1.orca_max_router import max_router

app = FastAPI(
    title="ORCA Trading System API",
    description="High-Performance Trading API optimized for HFT and Medium-Frequency Trading",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(trading_router, prefix="/api/v1", tags=["HFT Trading"])
app.include_router(hedge_router, prefix="/api/v1", tags=["Hedge Algorithm"])  # No /trading prefix for hedge endpoint
app.include_router(max_router, prefix="/api/v1", tags=["Max Trading Bot"])


# Pydantic models
class BotRequest(BaseModel):
    accountName: str
    mode: str
    contract: str
    dateFrom: str
    dateTo: str
    maxMode: str
    point_key: str
    exit_strategy_key: str
    notes: Optional[str] = None


class TradeResult(BaseModel):
    time: str
    price: float
    action: str
    profit: Optional[float] = None


class BotResponse(BaseModel):
    status: str
    message: str
    timestamp: str
    request: Dict[str, Any]
    results: List[Dict[str, Any]]


# Mock trading bot function
async def run_trading_bot(request: BotRequest) -> BotResponse:
    # This is where you would integrate with your actual trading bot
    # For now, we'll return mock data
    import time
    time.sleep(2)  # Simulate processing time

    return BotResponse(
        status="success",
        message="Bot execution completed successfully",
        timestamp=datetime.utcnow().isoformat(),
        request=request.dict(),
        results=[
            {"time": "09:30", "price": 200.50, "action": "BUY", "profit": None},
            {"time": "10:15", "price": 152.30, "action": "SELL", "profit": 1.80}
        ]
    )


# API Endpoints
@app.post("/api/run-bot/", response_model=BotResponse)
async def run_bot(request: BotRequest):
    try:
        result = await run_trading_bot(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health/")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)