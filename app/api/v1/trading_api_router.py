"""
High-Performance Trading API Router
Optimized for HFT (High-Frequency Trading) and Medium-Frequency Trading Bots

Features:
- Redis caching for frequently accessed data
- Minimal response payloads
- Fast response times (<50ms target)
- Batch operations support
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from loguru import logger
import time
from datetime import datetime, timedelta

from app.services.orca_redis.client import get_redis_client
from app.services.tradingview.broker import TradingViewTradovateBroker
import json

# Create router
trading_router = APIRouter(prefix="/trading", tags=["HFT Trading API"])

# Cache TTL settings (in seconds)
CACHE_TTL_ACCOUNTS = 300  # 5 minutes - accounts don't change often
CACHE_TTL_POSITIONS = 1  # 1 second - positions change frequently
CACHE_TTL_ORDERS = 1  # 1 second - orders change frequently
CACHE_TTL_BALANCE = 2  # 2 seconds - balance changes with trades


# ============================================================================
# Response Models (Minimal for Speed)
# ============================================================================

class AccountInfo(BaseModel):
    """Minimal account info for fast response"""
    name: str
    id: str
    active: bool = True

class AccountListResponse(BaseModel):
    """Fast account list response"""
    accounts: List[AccountInfo]
    count: int
    cached: bool
    timestamp: float

class PositionInfo(BaseModel):
    """Minimal position info"""
    id: str
    account_id: str
    instrument: str
    quantity: int
    side: str
    avg_price: float
    unrealized_pnl: float
    
class PositionListResponse(BaseModel):
    """Fast position list response"""
    positions: List[PositionInfo]
    count: int
    cached: bool
    timestamp: float

class OrderInfo(BaseModel):
    """Minimal order info"""
    order_id: str
    account_id: str
    instrument: str
    side: str
    quantity: int
    price: float
    status: str
    order_type: str

class OrderListResponse(BaseModel):
    """Fast order list response"""
    orders: List[OrderInfo]
    count: int
    cached: bool
    timestamp: float

class OrderIDListResponse(BaseModel):
    """Ultra-fast order ID only response"""
    order_ids: List[str]
    count: int
    cached: bool
    timestamp: float

class PositionIDListResponse(BaseModel):
    """Ultra-fast position ID only response"""
    position_ids: List[str]
    count: int
    cached: bool
    timestamp: float

class BalanceInfo(BaseModel):
    """Account balance info"""
    account_id: str
    account_name: str
    balance: float
    net_liquidating_value: float
    cash_balance: float
    open_pl: float
    realized_pl: float

class BalanceListResponse(BaseModel):
    """Fast balance response for all accounts"""
    balances: List[BalanceInfo]
    total_balance: float
    count: int
    cached: bool
    timestamp: float


# ============================================================================
# Helper Functions
# ============================================================================

def get_broker_instance(account_name: str = "PAAPEX2666680000001"):
    """Get broker instance with Redis token"""
    redis_client = get_redis_client()
    if not redis_client:
        raise HTTPException(status_code=503, detail="Redis unavailable")
    
    try:
        broker = TradingViewTradovateBroker(
            redis_client=redis_client,
            account_name=account_name,
            base_url="https://tv-demo.tradovateapi.com"
        )
        return broker
    except Exception as e:
        logger.error(f"Failed to initialize broker: {e}")
        raise HTTPException(status_code=503, detail=f"Broker unavailable: {str(e)}")


def get_cache_key(endpoint: str, *args) -> str:
    """Generate cache key for Redis"""
    return f"hft:{endpoint}:{':'.join(map(str, args))}"


def get_from_cache(cache_key: str):
    """Get data from Redis cache"""
    try:
        redis_client = get_redis_client()
        if redis_client:
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
    except Exception as e:
        logger.warning(f"Cache read error: {e}")
    return None


def set_to_cache(cache_key: str, data: Any, ttl: int):
    """Set data to Redis cache with TTL"""
    try:
        redis_client = get_redis_client()
        if redis_client:
            redis_client.setex(cache_key, ttl, json.dumps(data))
    except Exception as e:
        logger.warning(f"Cache write error: {e}")


# ============================================================================
# API ENDPOINTS
# ============================================================================

@trading_router.get("/accounts", response_model=AccountListResponse)
async def get_all_accounts(
    use_cache: bool = Query(True, description="Use cached data if available"),
    account_name: str = Query("PAAPEX2666680000001", description="Account name for authentication")
):
    """
    Get all accounts in the Tradovate user.
    
    - **Optimized for HFT**: Cached for 5 minutes
    - **Response time**: <50ms (cached), <500ms (fresh)
    - **Use case**: Account discovery, multi-account trading
    """
    start_time = time.time()
    cache_key = get_cache_key("accounts", account_name)
    
    # Try cache first
    if use_cache:
        cached_data = get_from_cache(cache_key)
        if cached_data:
            cached_data["cached"] = True
            cached_data["timestamp"] = time.time()
            logger.info(f"Accounts cache hit - {(time.time() - start_time)*1000:.2f}ms")
            return cached_data
    
    # Fetch fresh data
    try:
        broker = get_broker_instance(account_name)
        accounts_raw = broker.get_all_accounts()
        
        accounts = [
            AccountInfo(
                name=acc.get("name", ""),
                id=acc.get("id", ""),
                active=acc.get("active", True)
            )
            for acc in accounts_raw
        ]
        
        response_data = {
            "accounts": [acc.dict() for acc in accounts],
            "count": len(accounts),
            "cached": False,
            "timestamp": time.time()
        }
        
        # Cache for future requests
        set_to_cache(cache_key, response_data, CACHE_TTL_ACCOUNTS)
        
        elapsed_ms = (time.time() - start_time) * 1000
        logger.info(f"Accounts fetched fresh - {elapsed_ms:.2f}ms")
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error fetching accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@trading_router.get("/positions", response_model=PositionListResponse)
async def get_all_positions(
    use_cache: bool = Query(False, description="Use cached data (not recommended for HFT)"),
    account_ids: Optional[str] = Query(None, description="Comma-separated account IDs (e.g., D17158695,D17159229)"),
    account_name: str = Query("PAAPEX2666680000001", description="Account name for authentication")
):
    """
    Get all active positions across accounts.
    
    - **Optimized for HFT**: Cache TTL = 1s (very short for real-time data)
    - **Response time**: <100ms (cached), <800ms (fresh)
    - **Use case**: Position monitoring, risk management, PnL tracking
    """
    start_time = time.time()
    cache_key = get_cache_key("positions", account_name, account_ids or "all")
    
    # Try cache (1 second TTL for HFT)
    if use_cache:
        cached_data = get_from_cache(cache_key)
        if cached_data:
            cached_data["cached"] = True
            cached_data["timestamp"] = time.time()
            logger.info(f"Positions cache hit - {(time.time() - start_time)*1000:.2f}ms")
            return cached_data
    
    # Fetch fresh data
    try:
        broker = get_broker_instance(account_name)
        
        # Get target account IDs
        if account_ids:
            target_account_ids = account_ids.split(",")
        else:
            # Get all accounts
            accounts = broker.get_all_accounts()
            target_account_ids = [acc["id"] for acc in accounts]
        
        # Fetch positions for each account
        all_positions = []
        for acc_id in target_account_ids:
            try:
                positions_raw = broker.get_positions(acc_id)
                if positions_raw:
                    for pos in positions_raw:
                        all_positions.append(
                            PositionInfo(
                                id=pos.id,
                                account_id=acc_id,
                                instrument=pos.contractId,
                                quantity=abs(pos.netPos),
                                side="long" if pos.netPos > 0 else "short",
                                avg_price=pos.avgPrice,
                                unrealized_pnl=pos.unrealizedPl
                            )
                        )
            except Exception as e:
                logger.warning(f"Error fetching positions for account {acc_id}: {e}")
                continue
        
        response_data = {
            "positions": [pos.dict() for pos in all_positions],
            "count": len(all_positions),
            "cached": False,
            "timestamp": time.time()
        }
        
        # Cache for 1 second (HFT needs fresh data)
        set_to_cache(cache_key, response_data, CACHE_TTL_POSITIONS)
        
        elapsed_ms = (time.time() - start_time) * 1000
        logger.info(f"Positions fetched - {len(all_positions)} positions - {elapsed_ms:.2f}ms")
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error fetching positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@trading_router.get("/orders/pending", response_model=OrderListResponse)
async def get_pending_orders(
    use_cache: bool = Query(False, description="Use cached data (not recommended for HFT)"),
    account_ids: Optional[str] = Query(None, description="Comma-separated account IDs"),
    account_name: str = Query("PAAPEX2666680000001", description="Account name for authentication")
):
    """
    Get all pending orders across accounts.
    
    - **Optimized for HFT**: Cache TTL = 1s
    - **Response time**: <100ms (cached), <1000ms (fresh)
    - **Use case**: Order management, execution monitoring
    """
    start_time = time.time()
    cache_key = get_cache_key("orders:pending", account_name, account_ids or "all")
    
    # Try cache
    if use_cache:
        cached_data = get_from_cache(cache_key)
        if cached_data:
            cached_data["cached"] = True
            cached_data["timestamp"] = time.time()
            logger.info(f"Pending orders cache hit - {(time.time() - start_time)*1000:.2f}ms")
            return cached_data
    
    # Fetch fresh data
    try:
        broker = get_broker_instance(account_name)
        
        # Get target account IDs
        if account_ids:
            target_account_ids = account_ids.split(",")
        else:
            accounts = broker.get_all_accounts()
            target_account_ids = [acc["id"] for acc in accounts]
        
        # Fetch orders for each account
        all_orders = []
        pending_statuses = ["Working", "Pending", "Queued"]
        
        for acc_id in target_account_ids:
            try:
                orders_raw = broker.get_orders(acc_id)
                if orders_raw:
                    for order in orders_raw:
                        # Filter only pending orders
                        if order.status in pending_statuses:
                            all_orders.append(
                                OrderInfo(
                                    order_id=str(order.id),
                                    account_id=acc_id,
                                    instrument=order.instrument,
                                    side=order.side,
                                    quantity=order.qty,
                                    price=order.limitPrice or order.stopPrice or 0.0,
                                    status=order.status,
                                    order_type=order.orderType
                                )
                            )
            except Exception as e:
                logger.warning(f"Error fetching orders for account {acc_id}: {e}")
                continue
        
        response_data = {
            "orders": [order.dict() for order in all_orders],
            "count": len(all_orders),
            "cached": False,
            "timestamp": time.time()
        }
        
        # Cache for 1 second
        set_to_cache(cache_key, response_data, CACHE_TTL_ORDERS)
        
        elapsed_ms = (time.time() - start_time) * 1000
        logger.info(f"Pending orders fetched - {len(all_orders)} orders - {elapsed_ms:.2f}ms")
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error fetching pending orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@trading_router.get("/orders/pending/ids", response_model=OrderIDListResponse)
async def get_pending_order_ids(
    use_cache: bool = Query(False, description="Use cached data"),
    account_ids: Optional[str] = Query(None, description="Comma-separated account IDs"),
    account_name: str = Query("PAAPEX2666680000001", description="Account name for authentication")
):
    """
    Get only the IDs of pending orders (ultra-fast endpoint for HFT).
    
    - **Optimized for HFT**: Minimal payload, <50ms response time
    - **Use case**: Quick order existence checks, cancellation prep
    """
    start_time = time.time()
    
    # Get full order data (from cache if possible)
    orders_response = await get_pending_orders(use_cache, account_ids, account_name)
    
    # Extract only IDs
    order_ids = [order["order_id"] for order in orders_response["orders"]]
    
    elapsed_ms = (time.time() - start_time) * 1000
    logger.info(f"Pending order IDs fetched - {len(order_ids)} IDs - {elapsed_ms:.2f}ms")
    
    return {
        "order_ids": order_ids,
        "count": len(order_ids),
        "cached": orders_response["cached"],
        "timestamp": time.time()
    }


@trading_router.get("/positions/ids", response_model=PositionIDListResponse)
async def get_position_ids(
    use_cache: bool = Query(False, description="Use cached data"),
    account_ids: Optional[str] = Query(None, description="Comma-separated account IDs"),
    account_name: str = Query("PAAPEX2666680000001", description="Account name for authentication")
):
    """
    Get only the IDs of active positions (ultra-fast endpoint for HFT).
    
    - **Optimized for HFT**: Minimal payload, <50ms response time
    - **Use case**: Quick position existence checks, closing prep
    """
    start_time = time.time()
    
    # Get full position data (from cache if possible)
    positions_response = await get_all_positions(use_cache, account_ids, account_name)
    
    # Extract only IDs
    position_ids = [pos["id"] for pos in positions_response["positions"]]
    
    elapsed_ms = (time.time() - start_time) * 1000
    logger.info(f"Position IDs fetched - {len(position_ids)} IDs - {elapsed_ms:.2f}ms")
    
    return {
        "position_ids": position_ids,
        "count": len(position_ids),
        "cached": positions_response["cached"],
        "timestamp": time.time()
    }


@trading_router.get("/balances", response_model=BalanceListResponse)
async def get_account_balances(
    use_cache: bool = Query(True, description="Use cached data"),
    account_ids: Optional[str] = Query(None, description="Comma-separated account IDs"),
    account_name: str = Query("PAAPEX2666680000001", description="Account name for authentication")
):
    """
    Get account balances for all accounts.
    
    - **Optimized for HFT**: Cache TTL = 2s
    - **Response time**: <100ms (cached), <1200ms (fresh)
    - **Use case**: Risk management, margin monitoring, account health
    """
    start_time = time.time()
    cache_key = get_cache_key("balances", account_name, account_ids or "all")
    
    # Try cache
    if use_cache:
        cached_data = get_from_cache(cache_key)
        if cached_data:
            cached_data["cached"] = True
            cached_data["timestamp"] = time.time()
            logger.info(f"Balances cache hit - {(time.time() - start_time)*1000:.2f}ms")
            return cached_data
    
    # Fetch fresh data
    try:
        broker = get_broker_instance(account_name)
        
        # Get target account IDs and names
        if account_ids:
            target_account_ids = account_ids.split(",")
            # Need to get account names
            all_accounts = broker.get_all_accounts()
            account_map = {acc["id"]: acc["name"] for acc in all_accounts}
        else:
            all_accounts = broker.get_all_accounts()
            account_map = {acc["id"]: acc["name"] for acc in all_accounts}
            target_account_ids = list(account_map.keys())
        
        # Fetch balance for each account
        all_balances = []
        total_balance = 0.0
        
        for acc_id in target_account_ids:
            try:
                state = broker.get_account_state(acc_id)
                if state:
                    balance_info = BalanceInfo(
                        account_id=acc_id,
                        account_name=account_map.get(acc_id, "Unknown"),
                        balance=state.netLiquidatingValue,
                        net_liquidating_value=state.netLiquidatingValue,
                        cash_balance=state.cashBalance,
                        open_pl=state.openRealizedPl,
                        realized_pl=state.realizedPl
                    )
                    all_balances.append(balance_info)
                    total_balance += state.netLiquidatingValue
            except Exception as e:
                logger.warning(f"Error fetching balance for account {acc_id}: {e}")
                continue
        
        response_data = {
            "balances": [bal.dict() for bal in all_balances],
            "total_balance": total_balance,
            "count": len(all_balances),
            "cached": False,
            "timestamp": time.time()
        }
        
        # Cache for 2 seconds
        set_to_cache(cache_key, response_data, CACHE_TTL_BALANCE)
        
        elapsed_ms = (time.time() - start_time) * 1000
        logger.info(f"Balances fetched - {len(all_balances)} accounts - {elapsed_ms:.2f}ms")
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error fetching balances: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Batch Endpoint (for maximum efficiency)
# ============================================================================

@trading_router.get("/batch/snapshot")
async def get_trading_snapshot(
    include_accounts: bool = Query(True),
    include_positions: bool = Query(True),
    include_orders: bool = Query(True),
    include_balances: bool = Query(True),
    use_cache: bool = Query(False, description="Use cached data where possible"),
    account_ids: Optional[str] = Query(None, description="Comma-separated account IDs"),
    account_name: str = Query("PAAPEX2666680000001", description="Account name for authentication")
):
    """
    Get a complete trading snapshot in a single call.
    
    - **Optimized for HFT**: Single request for all data
    - **Response time**: <200ms (cached), <2000ms (fresh)
    - **Use case**: Dashboard updates, monitoring systems, trading bots startup
    
    This endpoint reduces network overhead by combining multiple calls into one.
    """
    start_time = time.time()
    snapshot = {}
    
    try:
        if include_accounts:
            accounts_data = await get_all_accounts(use_cache, account_name)
            snapshot["accounts"] = accounts_data
        
        if include_positions:
            positions_data = await get_all_positions(use_cache, account_ids, account_name)
            snapshot["positions"] = positions_data
        
        if include_orders:
            orders_data = await get_pending_orders(use_cache, account_ids, account_name)
            snapshot["orders"] = orders_data
        
        if include_balances:
            balances_data = await get_account_balances(use_cache, account_ids, account_name)
            snapshot["balances"] = balances_data
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        snapshot["metadata"] = {
            "response_time_ms": elapsed_ms,
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat()
        }
        
        logger.info(f"Trading snapshot complete - {elapsed_ms:.2f}ms")
        
        return JSONResponse(content=snapshot)
        
    except Exception as e:
        logger.error(f"Error fetching trading snapshot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Health Check Endpoint
# ============================================================================

@trading_router.get("/health")
async def health_check():
    """
    Health check for the trading API.
    
    - Checks Redis connectivity
    - Checks broker availability
    - Returns response time metrics
    """
    start_time = time.time()
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "datetime": datetime.now().isoformat(),
        "checks": {}
    }
    
    # Check Redis
    try:
        redis_client = get_redis_client()
        redis_client.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Broker
    try:
        broker = get_broker_instance()
        health_status["checks"]["broker"] = "healthy"
    except Exception as e:
        health_status["checks"]["broker"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    elapsed_ms = (time.time() - start_time) * 1000
    health_status["response_time_ms"] = elapsed_ms
    
    return health_status
