import requests

BASE_URL = "http://localhost:8000/api/v1/hedge/start"
TIMEOUT = 30
HEADERS = {"Content-Type": "application/json"}

def test_validate_hedge_start_accepts_account_a_alias():
    # Common request payload template (except account_a_name/account_a)
    common_payload = {
        "account_b_name": "AccountB_Test_01",
        "instrument": "MNQ",
        "direction": "long",
        "entry_price": 21000.0,
        "quantity": 1,
        "tp_distance": 10.0,
        "sl_distance": 5.0,
        "hedge_distance": 2.0
    }

    for alias_field in ["account_a_name", "account_a"]:
        payload = common_payload.copy()
        payload[alias_field] = "AccountA_Test_01"

        try:
            response = requests.post(
                BASE_URL,
                json=payload,
                headers=HEADERS,
                timeout=TIMEOUT,
            )
        except requests.RequestException as e:
            assert False, f"Request failed for {alias_field} alias: {e}"

        # Validate status code
        assert response.status_code == 200, f"Expected 200 OK for {alias_field} alias, got {response.status_code}"

        json_resp = response.json()
        # Validate top-level status in response
        assert "status" in json_resp, f"'status' missing in response for {alias_field} alias"
        assert json_resp["status"] in ["success", "partial", "failed"], f"Unexpected status value for {alias_field} alias"

        # Validate both account results exist
        assert "account_a_result" in json_resp, f"'account_a_result' missing for {alias_field} alias"
        assert "account_b_result" in json_resp, f"'account_b_result' missing for {alias_field} alias"

        # Account A result checks
        a_result = json_resp["account_a_result"]
        assert a_result.get("account_name") == payload[alias_field], f"Account A name mismatch for {alias_field} alias"
        assert isinstance(a_result.get("status"), str), f"Account A status missing or invalid for {alias_field} alias"
        assert a_result.get("direction") == payload["direction"].lower(), f"Account A direction mismatch for {alias_field} alias"

        # Account B result checks
        b_result = json_resp["account_b_result"]
        assert b_result.get("account_name") == payload["account_b_name"], f"Account B name mismatch for {alias_field} alias"
        expected_opposite_direction = "short" if payload["direction"].lower() == "long" else "long"
        assert b_result.get("direction") == expected_opposite_direction, f"Account B direction mismatch for {alias_field} alias"

test_validate_hedge_start_accepts_account_a_alias()
