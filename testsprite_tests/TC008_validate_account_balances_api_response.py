import requests

BASE_URL = "http://localhost:8000/api/v1/trading/balances"
TIMEOUT = 30

def test_validate_account_balances_api_response():
    headers = {
        "Accept": "application/json"
    }
    try:
        response = requests.get(BASE_URL, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        assert False, f"Request to {BASE_URL} failed: {e}"

    # Validate response is JSON and structure expected
    try:
        data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    # The response should contain account balances and aggregated totals
    # Since the schema is not detailed in PRD, we check presence of typical fields or list and totals
    # Commonly balances API might return a list named 'balances' or 'accounts' and some summary fields
    # We assert data should be a dict
    assert isinstance(data, dict), "Response JSON should be an object"

    # Check that keys related to balances exist
    # We expect at minimum a list or dict of balances. Common might be 'balances' or 'accounts'
    possible_balance_keys = ['balances', 'accounts', 'total_balance', 'aggregated_totals']
    keys_found = set(data.keys())
    assert any(k in keys_found for k in possible_balance_keys), f"Response JSON keys missing expected balance-related keys: {possible_balance_keys}"

    # If balances or accounts present, check it is a list and contains expected fields
    balance_list_key = None
    for key in ['balances', 'accounts']:
        if key in data:
            balance_list_key = key
            break

    if balance_list_key:
        balances = data[balance_list_key]
        assert isinstance(balances, list), f"{balance_list_key} should be a list"
        if len(balances) > 0:
            # Check that each balance item includes at least an account identifier and balance amount fields (typical names: 'account_id', 'balance', 'currency')
            first_item = balances[0]
            assert isinstance(first_item, dict), f"Items in {balance_list_key} should be objects"
            # Check for keys that usually represent account and balance
            has_account_id = any(k.lower() in first_item for k in ['account_id', 'id', 'account'])
            has_balance_amount = any(k.lower() in first_item for k in ['balance', 'amount', 'total'])
            assert has_account_id, f"Balance items should contain an account identifier field"
            assert has_balance_amount, f"Balance items should contain a balance amount field"

    # Check aggregated totals if present - could be numeric fields in the root dict
    numeric_aggregated_keys = ['total_balance', 'aggregated_totals', 'total', 'sum']
    numeric_keys_found = [k for k in numeric_aggregated_keys if k in data]
    for key in numeric_keys_found:
        assert isinstance(data[key], (int, float)), f"Aggregated total field '{key}' should be numeric"

test_validate_account_balances_api_response()