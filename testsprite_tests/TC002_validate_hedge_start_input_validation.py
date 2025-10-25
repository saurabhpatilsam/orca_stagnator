import requests

BASE_URL = "http://localhost:8000/api/v1/hedge/start"
TIMEOUT = 30
HEADERS = {"Content-Type": "application/json"}

def validate_hedge_start_input_validation():
    invalid_test_cases = [
        # Negative quantity
        {
            "account_a_name": "AccountA1",
            "account_b_name": "AccountB1",
            "instrument": "MNQ",
            "direction": "long",
            "entry_price": 21000.25,
            "quantity": -1,
            "tp_distance": 5,
            "sl_distance": 2,
            "hedge_distance": 1,
            "expect_400": True
        },
        # Zero quantity
        {
            "account_a_name": "AccountA1",
            "account_b_name": "AccountB2",
            "instrument": "MNQ",
            "direction": "long",
            "entry_price": 21000.25,
            "quantity": 0,
            "tp_distance": 5,
            "sl_distance": 2,
            "hedge_distance": 1,
            "expect_400": True
        },
        # Zero entry price
        {
            "account_a_name": "AccountA1",
            "account_b_name": "AccountB3",
            "instrument": "MNQ",
            "direction": "long",
            "entry_price": 0,
            "quantity": 1,
            "tp_distance": 5,
            "sl_distance": 2,
            "hedge_distance": 1,
            "expect_400": True
        },
        # Negative entry price
        {
            "account_a_name": "AccountA1",
            "account_b_name": "AccountB4",
            "instrument": "MNQ",
            "direction": "long",
            "entry_price": -100,
            "quantity": 1,
            "tp_distance": 5,
            "sl_distance": 2,
            "hedge_distance": 1,
            "expect_400": True
        },
        # Zero tp_distance (allowed)
        {
            "account_a_name": "AccountA1",
            "account_b_name": "AccountB5",
            "instrument": "MNQ",
            "direction": "long",
            "entry_price": 21000.25,
            "quantity": 1,
            "tp_distance": 0,
            "sl_distance": 2,
            "hedge_distance": 1,
            "expect_400": False
        },
        # Negative tp_distance (invalid)
        {
            "account_a_name": "AccountA1",
            "account_b_name": "AccountB6",
            "instrument": "MNQ",
            "direction": "long",
            "entry_price": 21000.25,
            "quantity": 1,
            "tp_distance": -1,
            "sl_distance": 2,
            "hedge_distance": 1,
            "expect_400": True
        },
        # Negative sl_distance (invalid)
        {
            "account_a_name": "AccountA1",
            "account_b_name": "AccountB7",
            "instrument": "MNQ",
            "direction": "long",
            "entry_price": 21000.25,
            "quantity": 1,
            "tp_distance": 5,
            "sl_distance": -2,
            "hedge_distance": 1,
            "expect_400": True
        },
        # Invalid direction (uppercase, valid directions are 'long' or 'short' only)
        {
            "account_a_name": "AccountA1",
            "account_b_name": "AccountB8",
            "instrument": "MNQ",
            "direction": "LONG",
            "entry_price": 21000.25,
            "quantity": 1,
            "tp_distance": 5,
            "sl_distance": 2,
            "hedge_distance": 1,
            "expect_400": True
        },
        # Invalid direction (not long or short)
        {
            "account_a_name": "AccountA1",
            "account_b_name": "AccountB9",
            "instrument": "MNQ",
            "direction": "up",
            "entry_price": 21000.25,
            "quantity": 1,
            "tp_distance": 5,
            "sl_distance": 2,
            "hedge_distance": 1,
            "expect_400": True
        },
        # Identical account names
        {
            "account_a_name": "SameAccount",
            "account_b_name": "SameAccount",
            "instrument": "MNQ",
            "direction": "long",
            "entry_price": 21000.25,
            "quantity": 1,
            "tp_distance": 5,
            "sl_distance": 2,
            "hedge_distance": 1,
            "expect_400": True
        },
    ]

    for i, test_case in enumerate(invalid_test_cases, start=1):
        payload = {k: v for k, v in test_case.items() if k != "expect_400"}
        expect_400 = test_case["expect_400"]
        try:
            response = requests.post(BASE_URL, json=payload, headers=HEADERS, timeout=TIMEOUT)
        except requests.RequestException as e:
            assert False, f"Test case #{i} failed with request exception: {e}"

        if expect_400:
            assert response.status_code == 400, f"Test case #{i} expected 400 but got {response.status_code}. Payload: {payload}"
        else:
            assert response.status_code == 200, f"Test case #{i} expected 200 but got {response.status_code}. Payload: {payload}"

validate_hedge_start_input_validation()
