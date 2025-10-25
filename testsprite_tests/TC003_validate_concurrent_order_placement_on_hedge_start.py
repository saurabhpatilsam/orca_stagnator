import requests
import time

BASE_URL = "http://localhost:8000/api/v1/hedge/start"
TIMEOUT = 30  # seconds

def validate_concurrent_order_placement_on_hedge_start():
    # Prepare hedge order request payload for concurrent order placement test
    # Use two distinct accounts with assumed valid names and tokens in Redis
    payload = {
        "account_a_name": "TEST_ACCOUNT_A_12345",
        "account_b_name": "TEST_ACCOUNT_B_54321",
        "instrument": "MNQ",          # MNQ uses 0.25 tick size
        "direction": "long",
        "entry_price": 21000.13,       # Not rounded intentionally to verify backend rounding
        "quantity": 1,
        "tp_distance": 10,
        "sl_distance": 5,
        "hedge_distance": 2            # Price difference for account B entry
    }
    headers = {
        "Content-Type": "application/json"
    }

    start_time = time.time()
    try:
        response = requests.post(BASE_URL, json=payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    duration = time.time() - start_time

    assert response.status_code == 200, f"Expected status 200 OK but got {response.status_code}"
    data = response.json()

    # Validate overall status
    assert data.get("status") in ["success", "partial"], "Hedge order placement failed or returned unexpected status"

    # Validate account A result presence and correctness
    account_a_result = data.get("account_a_result")
    assert account_a_result is not None, "Missing account_a_result in response"
    assert account_a_result.get("account_name") == payload["account_a_name"], "account_a_name mismatch"
    assert "order_id" in account_a_result and account_a_result["order_id"], "Missing order_id for account A"
    assert account_a_result.get("direction") == payload["direction"].lower(), "Direction mismatch for account A"
    # entry_price should be rounded according to MNQ tick size (0.25). 21000.13 rounds to 21000.25
    rounded_entry_a = round(payload["entry_price"] / 0.25) * 0.25
    assert abs(account_a_result.get("entry_price", 0) - rounded_entry_a) < 1e-6, "Entry price not correctly rounded for account A"
    # Validate stop_loss and take_profit presence and positive numbers
    assert isinstance(account_a_result.get("stop_loss"), (int, float)) and account_a_result["stop_loss"] >= 0, "Invalid stop_loss for account A"
    assert isinstance(account_a_result.get("take_profit"), (int, float)) and account_a_result["take_profit"] >= 0, "Invalid take_profit for account A"
    # Status in account A result should be success or partial
    assert account_a_result.get("status") in ["success", "partial"], "Order status for account A not success or partial"
    # error_message should be string or None/empty
    assert "error_message" in account_a_result, "Missing error_message field for account A"

    # Validate account B result presence and correctness
    account_b_result = data.get("account_b_result")
    assert account_b_result is not None, "Missing account_b_result in response"
    assert account_b_result.get("account_name") == payload["account_b_name"], "account_b_name mismatch"
    assert "order_id" in account_b_result and account_b_result["order_id"], "Missing order_id for account B"
    # Account B direction is opposite of account A
    expected_direction_b = "short" if payload["direction"].lower() == "long" else "long"
    assert account_b_result.get("direction") == expected_direction_b, "Direction mismatch for account B"
    # Account B entry price = entry_price 7 hedge_distance; account_a is long so account_b entry price = entry_price + hedge_distance
    expected_entry_b = payload["entry_price"] + payload["hedge_distance"]
    rounded_entry_b = round(expected_entry_b / 0.25) * 0.25
    assert abs(account_b_result.get("entry_price", 0) - rounded_entry_b) < 1e-6, "Entry price not correctly rounded for account B"
    assert isinstance(account_b_result.get("stop_loss"), (int, float)) and account_b_result["stop_loss"] >= 0, "Invalid stop_loss for account B"
    assert isinstance(account_b_result.get("take_profit"), (int, float)) and account_b_result["take_profit"] >= 0, "Invalid take_profit for account B"
    assert account_b_result.get("status") in ["success", "partial"], "Order status for account B not success or partial"
    assert "error_message" in account_b_result, "Missing error_message field for account B"

    # Validate timestamp presence and is a number
    assert isinstance(data.get("timestamp"), (int, float)), "Missing or invalid timestamp"

    # Assert reasonable API response time indicating concurrency (e.g. must be less than 5 seconds, adjust if needed)
    assert duration < 5, f"API response took too long ({duration:.2f}s), concurrency may not be working properly"

validate_concurrent_order_placement_on_hedge_start()
