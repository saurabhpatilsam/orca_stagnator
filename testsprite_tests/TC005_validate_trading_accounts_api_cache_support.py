import requests

BASE_URL = "http://localhost:8000/api/v1/trading/accounts"
TIMEOUT = 30

def test_validate_trading_accounts_api_cache_support():
    headers = {
        "Accept": "application/json"
    }

    # Test with use_cache=true
    params_true = {
        "use_cache": "true"
    }
    try:
        response_true = requests.get(BASE_URL, headers=headers, params=params_true, timeout=TIMEOUT)
        assert response_true.status_code == 200, f"Expected 200, got {response_true.status_code}"
        data_true = response_true.json()

        assert isinstance(data_true, dict), "Response is not a JSON object"
        assert "accounts" in data_true, "'accounts' key missing in response"
        assert isinstance(data_true["accounts"], list), "'accounts' is not a list"
        assert "count" in data_true and isinstance(data_true["count"], int), "'count' key missing or not int"
        assert "cached" in data_true and isinstance(data_true["cached"], bool), "'cached' key missing or not bool"
        assert data_true["cached"] is True, "Expected cached to be True when use_cache=true"
        assert "timestamp" in data_true and isinstance(data_true["timestamp"], (int, float)), "'timestamp' key missing or wrong type"

        for account in data_true["accounts"]:
            assert "name" in account and isinstance(account["name"], str), "Account missing 'name' or not string"
            assert "id" in account and isinstance(account["id"], str), "Account missing 'id' or not string"
            assert "active" in account and isinstance(account["active"], bool), "Account missing 'active' or not bool"

    except requests.RequestException as e:
        assert False, f"Request failed with exception: {e}"

    # Test with use_cache=false
    params_false = {
        "use_cache": "false"
    }
    try:
        response_false = requests.get(BASE_URL, headers=headers, params=params_false, timeout=TIMEOUT)
        assert response_false.status_code == 200, f"Expected 200, got {response_false.status_code}"
        data_false = response_false.json()

        assert isinstance(data_false, dict), "Response is not a JSON object"
        assert "accounts" in data_false, "'accounts' key missing in response"
        assert isinstance(data_false["accounts"], list), "'accounts' is not a list"
        assert "count" in data_false and isinstance(data_false["count"], int), "'count' key missing or not int"
        assert "cached" in data_false and isinstance(data_false["cached"], bool), "'cached' key missing or not bool"
        assert data_false["cached"] is False, "Expected cached to be False when use_cache=false"
        assert "timestamp" in data_false and isinstance(data_false["timestamp"], (int, float)), "'timestamp' key missing or wrong type"

        for account in data_false["accounts"]:
            assert "name" in account and isinstance(account["name"], str), "Account missing 'name' or not string"
            assert "id" in account and isinstance(account["id"], str), "Account missing 'id' or not string"
            assert "active" in account and isinstance(account["active"], bool), "Account missing 'active' or not bool"

    except requests.RequestException as e:
        assert False, f"Request failed with exception: {e}"

test_validate_trading_accounts_api_cache_support()