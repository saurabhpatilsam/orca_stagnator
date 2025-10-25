import requests
from requests.exceptions import RequestException, Timeout

BASE_URL = "http://localhost:8000/api/v1/trading"
TIMEOUT = 30

def test_validate_positions_api_minimal_latency_response():
    # Step 1: Get all trading accounts to obtain active account IDs
    accounts_url = f"{BASE_URL}/accounts"
    try:
        accounts_resp = requests.get(accounts_url, params={"use_cache": True}, timeout=TIMEOUT)
        accounts_resp.raise_for_status()
    except (RequestException, Timeout) as e:
        assert False, f"Failed to get accounts: {e}"

    accounts_data = accounts_resp.json()
    assert "accounts" in accounts_data, "Response missing 'accounts' field"
    assert isinstance(accounts_data["accounts"], list), "'accounts' should be a list"

    # Filter active accounts and extract their IDs
    active_account_ids = [acc["id"] for acc in accounts_data["accounts"] if acc.get("active")]
    assert len(active_account_ids) > 0, "No active accounts found to test positions API"

    # Prepare comma-separated account_ids string
    account_ids_param = ",".join(active_account_ids[:5])  # limit to 5 accounts for test conciseness

    # Step 2: Request positions for these account IDs
    positions_url = f"{BASE_URL}/positions"
    params = {
        "account_ids": account_ids_param,
        "use_cache": False  # per PRD default for minimal latency testing
    }
    try:
        positions_resp = requests.get(positions_url, params=params, timeout=TIMEOUT)
        positions_resp.raise_for_status()
    except (RequestException, Timeout) as e:
        assert False, f"Failed to get positions: {e}"

    positions_data = positions_resp.json()
    # Validate we received a list or dict (API doc states "List of positions" but schema isn't explicit)
    assert positions_data is not None, "Positions response is empty or None"

    # Basic validations: if positions returned, check structure for each
    if isinstance(positions_data, list):
        for pos in positions_data:
            assert "accountId" in pos or "account_id" in pos or "accountId" in pos, "Position missing account ID"
            assert "quantity" in pos or "qty" in pos or "size" in pos, "Position missing quantity/size"
    elif isinstance(positions_data, dict):
        # Sometimes positions might be wrapped in a dict with keys like 'positions' or similar
        if "positions" in positions_data:
            assert isinstance(positions_data["positions"], list), "'positions' key is not a list"
        else:
            # just assert keys presence that can represent position info
            keys = positions_data.keys()
            assert any(k.lower().find("account") >= 0 for k in keys), "No account related field in positions response"
    else:
        assert False, f"Unexpected data type for positions response: {type(positions_data)}"

    # Latency check: ensure response time is minimal (e.g. below 1 second)
    # Note: This is an indicative check; adjust threshold if environment differs
    response_time = positions_resp.elapsed.total_seconds()
    assert response_time < 1.0, f"Positions API response latency too high: {response_time:.3f} seconds"

test_validate_positions_api_minimal_latency_response()