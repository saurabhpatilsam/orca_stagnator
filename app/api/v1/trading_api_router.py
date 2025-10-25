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
from pydantic import BaseModel, Field, ConfigDict
from loguru import logger
import time
import asyncio
from datetime import datetime, timedelta

from app.services.orca_redis.client import get_redis_client
from app.services.tradingview.broker import TradingViewTradovateBroker
from app.services.orca_max.schemas import Order
import json

# Create routers
trading_router = APIRouter(prefix="/trading", tags=["HFT Trading API"])
hedge_router = APIRouter(tags=["Hedge Algorithm"])  # Separate router without /trading prefix

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
# Hedge Algorithm Models
# ============================================================================

class HedgeStartRequest(BaseModel):
    """Request model for starting hedge algorithm"""
    # Accept both account_a_name and account_a for backward compatibility
    account_a_name: str = Field(validation_alias="account_a")
    account_b_name: str = Field(validation_alias="account_b")
    instrument: str
    direction: str  # "long" or "short" for Account A
    entry_price: float
    quantity: int
    tp_distance: float
    sl_distance: float
    hedge_distance: float = 0.0
    
    model_config = ConfigDict(
        populate_by_name=True,  # Allow both field name and validation_alias
        protected_namespaces=()  # Disable protected namespace warnings
    )

class HedgeOrderResult(BaseModel):
    """Result of a single hedge order"""
    account_name: str
    account_id: str
    order_id: Optional[str]
    status: str  # "success" or "failed"
    error_message: Optional[str]
    direction: str  # "long" or "short"
    entry_price: float
    stop_loss: float
    take_profit: float

class HedgeStartResponse(BaseModel):
    """Response model for hedge algorithm start"""
    status: str  # "success", "partial", or "failed"
    account_a_result: HedgeOrderResult
    account_b_result: HedgeOrderResult
    timestamp: float


# ============================================================================
# Helper Functions
# ============================================================================

# Instrument tick sizes (minimum price increment)
INSTRUMENT_TICK_SIZES = {
    "NQ": 0.25,      # E-mini Nasdaq
    "MNQ": 0.25,     # Micro E-mini Nasdaq
    "ES": 0.25,      # E-mini S&P 500
    "MES": 0.25,     # Micro E-mini S&P 500
    "YM": 1.0,       # E-mini Dow
    "MYM": 1.0,      # Micro E-mini Dow
    "RTY": 0.10,     # E-mini Russell 2000
    "M2K": 0.10,     # Micro E-mini Russell 2000
    # Add more instruments as needed
}

def get_tick_size(instrument: str) -> float:
    """Get tick size for an instrument. Returns 0.25 as default for futures."""
    # Extract base symbol (remove contract month codes like Z5, H6, etc.)
    base_symbol = instrument.rstrip("0123456789FGHJKMNQUVXZ")
    return INSTRUMENT_TICK_SIZES.get(base_symbol, 0.25)

def round_to_tick(price: float, tick_size: float) -> float:
    """Round price to the nearest tick size."""
    if tick_size <= 0:
        return price
    return round(price / tick_size) * tick_size

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
        
        # Fetch positions for each account CONCURRENTLY (HFT optimization)
        async def fetch_positions_for_account(acc_id: str):
            """Fetch positions for a single account"""
            try:
                positions_raw = await asyncio.to_thread(broker.get_positions, acc_id)
                account_positions = []
                if positions_raw:
                    for pos in positions_raw:
                        account_positions.append(
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
                return account_positions
            except Exception as e:
                logger.warning(f"Error fetching positions for account {acc_id}: {e}")
                return []
        
        # Execute all fetches concurrently for maximum speed
        position_results = await asyncio.gather(
            *[fetch_positions_for_account(acc_id) for acc_id in target_account_ids],
            return_exceptions=False
        )
        
        # Flatten results
        all_positions = [pos for positions in position_results for pos in positions]
        
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
        
        # Fetch orders for each account CONCURRENTLY (HFT optimization)
        pending_statuses = ["Working", "Pending", "Queued"]
        
        async def fetch_orders_for_account(acc_id: str):
            """Fetch orders for a single account"""
            try:
                orders_raw = await asyncio.to_thread(broker.get_orders, acc_id)
                account_orders = []
                if orders_raw:
                    for order in orders_raw:
                        # Filter only pending orders
                        if order.status in pending_statuses:
                            account_orders.append(
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
                return account_orders
            except Exception as e:
                logger.warning(f"Error fetching orders for account {acc_id}: {e}")
                return []
        
        # Execute all fetches concurrently for maximum speed
        order_results = await asyncio.gather(
            *[fetch_orders_for_account(acc_id) for acc_id in target_account_ids],
            return_exceptions=False
        )
        
        # Flatten results
        all_orders = [order for orders in order_results for order in orders]
        
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
        
        # Fetch balance for each account CONCURRENTLY (HFT optimization)
        async def fetch_balance_for_account(acc_id: str):
            """Fetch balance for a single account"""
            try:
                state = await asyncio.to_thread(broker.get_account_state, acc_id)
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
                    return balance_info
                return None
            except Exception as e:
                logger.warning(f"Error fetching balance for account {acc_id}: {e}")
                return None
        
        # Execute all fetches concurrently for maximum speed
        balance_results = await asyncio.gather(
            *[fetch_balance_for_account(acc_id) for acc_id in target_account_ids],
            return_exceptions=False
        )
        
        # Filter out None results and calculate total
        all_balances = [bal for bal in balance_results if bal is not None]
        total_balance = sum(bal.net_liquidating_value for bal in all_balances)
        
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


# ============================================================================
# Hedge Algorithm Endpoint
# ============================================================================

@hedge_router.post("/hedge/start", response_model=HedgeStartResponse)
async def start_hedge_algorithm(request: HedgeStartRequest):
    """
    Start a hedge algorithm that places opposite trades on two accounts.
    
    The algorithm:
    1. Places a trade on Account A at the specified entry price
    2. Places an opposite trade on Account B with hedge distance applied
    3. Sets take profit and stop loss for both accounts
    
    Hedge Distance Logic:
    - If hedge_distance = 0: Both accounts enter at same price
    - If hedge_distance > 0 and Account A is LONG:
        - Account A enters LONG at entry_price
        - Account B enters SHORT at entry_price - hedge_distance
    - If hedge_distance > 0 and Account A is SHORT:
        - Account A enters SHORT at entry_price
        - Account B enters LONG at entry_price + hedge_distance
    
    Returns detailed results for both order placements.
    """
    start_time = time.time()
    
    try:
        # Log incoming request
        logger.info(f"Starting hedge algorithm: {request.dict()}")
        
        # Step 1: Normalize and validate inputs
        direction = request.direction.lower()
        
        # Validate direction
        if direction not in ["long", "short"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid direction: '{request.direction}'. Must be 'long' or 'short'"
            )
        
        # Validate positive values
        if request.quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
        if request.entry_price <= 0:
            raise HTTPException(status_code=400, detail="Entry price must be greater than 0")
        if request.tp_distance < 0:
            raise HTTPException(status_code=400, detail="TP distance cannot be negative")
        if request.sl_distance < 0:
            raise HTTPException(status_code=400, detail="SL distance cannot be negative")
        if request.hedge_distance < 0:
            raise HTTPException(status_code=400, detail="Hedge distance cannot be negative")
        
        # Prevent same account for both A and B
        if request.account_a_name == request.account_b_name:
            raise HTTPException(
                status_code=400, 
                detail="Account A and Account B must be different accounts"
            )
        
        # Step 2: Initialize separate broker instances for each account
        broker_a = get_broker_instance(request.account_a_name)
        broker_b = get_broker_instance(request.account_b_name)
        
        # Get all accounts to validate and get IDs (using broker_a is sufficient for validation)
        accounts = broker_a.get_all_accounts()
        if not accounts:
            raise HTTPException(status_code=503, detail="Failed to fetch accounts")
        
        # Create account mapping
        account_map = {acc["name"]: acc["id"] for acc in accounts}
        
        # Validate both accounts exist
        if request.account_a_name not in account_map:
            raise HTTPException(status_code=400, detail=f"Account not found: {request.account_a_name}")
        if request.account_b_name not in account_map:
            raise HTTPException(status_code=400, detail=f"Account not found: {request.account_b_name}")
        
        # Get account IDs
        account_a_id = account_map[request.account_a_name]
        account_b_id = account_map[request.account_b_name]
        
        logger.info(f"Account A: {request.account_a_name} (ID: {account_a_id})")
        logger.info(f"Account B: {request.account_b_name} (ID: {account_b_id})")
        
        # Step 3: Calculate entry prices
        account_a_entry = request.entry_price
        
        # Calculate Account B entry based on hedge distance
        if direction == "long":
            account_b_entry = request.entry_price - request.hedge_distance
        else:  # short
            account_b_entry = request.entry_price + request.hedge_distance
        
        # Validate Account B entry is positive
        if account_b_entry <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"Computed Account B entry price ({account_b_entry}) is not positive. "
                       f"Adjust entry_price or hedge_distance."
            )
        
        logger.info(f"Entry prices - Account A: {account_a_entry}, Account B: {account_b_entry}")
        
        # Step 4: Calculate TP/SL for Account A
        if direction == "long":
            account_a_tp = account_a_entry + request.tp_distance
            account_a_sl = account_a_entry - request.sl_distance
        else:  # short
            account_a_tp = account_a_entry - request.tp_distance
            account_a_sl = account_a_entry + request.sl_distance
        
        # Step 5: Calculate TP/SL for Account B (opposite direction)
        account_b_direction = "short" if direction == "long" else "long"
        
        if account_b_direction == "long":
            account_b_tp = account_b_entry + request.tp_distance
            account_b_sl = account_b_entry - request.sl_distance
        else:  # short
            account_b_tp = account_b_entry - request.tp_distance
            account_b_sl = account_b_entry + request.sl_distance
        
        # Step 6: Round all prices to instrument's tick size
        tick_size = get_tick_size(request.instrument)
        logger.info(f"Using tick size {tick_size} for instrument {request.instrument}")
        
        account_a_entry = round_to_tick(account_a_entry, tick_size)
        account_a_tp = round_to_tick(account_a_tp, tick_size)
        account_a_sl = round_to_tick(account_a_sl, tick_size)
        
        account_b_entry = round_to_tick(account_b_entry, tick_size)
        account_b_tp = round_to_tick(account_b_tp, tick_size)
        account_b_sl = round_to_tick(account_b_sl, tick_size)
        
        logger.info(f"Account A ({direction}): Entry={account_a_entry}, TP={account_a_tp}, SL={account_a_sl}")
        logger.info(f"Account B ({account_b_direction}): Entry={account_b_entry}, TP={account_b_tp}, SL={account_b_sl}")
        
        # Step 7: Create Order objects
        order_a = Order(
            instrument=request.instrument,
            quantity=request.quantity,
            price=account_a_entry,
            position="buy" if direction == "long" else "sell",
            order_type="limit",
            stop_loss=account_a_sl,
            take_profit=account_a_tp,
            timestamp=datetime.now(),
            order_dict_all={}
        )
        
        order_b = Order(
            instrument=request.instrument,
            quantity=request.quantity,
            price=account_b_entry,
            position="sell" if direction == "long" else "buy",  # Opposite of Account A
            order_type="limit",
            stop_loss=account_b_sl,
            take_profit=account_b_tp,
            timestamp=datetime.now(),
            order_dict_all={}
        )
        
        # Step 8: Place orders concurrently to reduce latency and slippage risk
        order_a_id = None
        order_a_error = None
        order_b_id = None
        order_b_error = None
        
        # Define async wrapper functions for concurrent execution
        async def place_order_a():
            """Place order on Account A"""
            try:
                logger.info(f"Placing order on Account A ({request.account_a_name})...")
                order_id = await asyncio.to_thread(
                    broker_a.place_order, 
                    order=order_a, 
                    account_id=account_a_id
                )
                if order_id:
                    logger.info(f"Account A order placed successfully: {order_id}")
                    return order_id, None
                else:
                    error = "Order placement returned None"
                    logger.error(f"Account A order failed: {error}")
                    return None, error
            except Exception as e:
                logger.error(f"Account A order failed with exception: {e}")
                return None, str(e)
        
        async def place_order_b():
            """Place order on Account B"""
            try:
                logger.info(f"Placing order on Account B ({request.account_b_name})...")
                order_id = await asyncio.to_thread(
                    broker_b.place_order, 
                    order=order_b, 
                    account_id=account_b_id
                )
                if order_id:
                    logger.info(f"Account B order placed successfully: {order_id}")
                    return order_id, None
                else:
                    error = "Order placement returned None"
                    logger.error(f"Account B order failed: {error}")
                    return None, error
            except Exception as e:
                logger.error(f"Account B order failed with exception: {e}")
                return None, str(e)
        
        # Execute both order placements concurrently
        logger.info("Placing both orders concurrently...")
        results = await asyncio.gather(
            place_order_a(),
            place_order_b(),
            return_exceptions=False  # Exceptions are handled within wrapper functions
        )
        
        # Extract results
        order_a_id, order_a_error = results[0]
        order_b_id, order_b_error = results[1]
        
        # Step 9: Build response objects
        account_a_result = HedgeOrderResult(
            account_name=request.account_a_name,
            account_id=account_a_id,
            order_id=order_a_id,
            status="success" if order_a_id else "failed",
            error_message=order_a_error,
            direction=direction,
            entry_price=account_a_entry,
            stop_loss=account_a_sl,
            take_profit=account_a_tp
        )
        
        account_b_result = HedgeOrderResult(
            account_name=request.account_b_name,
            account_id=account_b_id,
            order_id=order_b_id,
            status="success" if order_b_id else "failed",
            error_message=order_b_error,
            direction=account_b_direction,
            entry_price=account_b_entry,
            stop_loss=account_b_sl,
            take_profit=account_b_tp
        )
        
        # Step 10: Determine overall status
        if order_a_id and order_b_id:
            overall_status = "success"
        elif order_a_id or order_b_id:
            overall_status = "partial"
        else:
            overall_status = "failed"
        
        # Step 11: Return response
        elapsed_ms = (time.time() - start_time) * 1000
        logger.info(f"Hedge algorithm completed in {elapsed_ms:.2f}ms with status: {overall_status}")
        
        return HedgeStartResponse(
            status=overall_status,
            account_a_result=account_a_result,
            account_b_result=account_b_result,
            timestamp=time.time()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Hedge algorithm failed with unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
