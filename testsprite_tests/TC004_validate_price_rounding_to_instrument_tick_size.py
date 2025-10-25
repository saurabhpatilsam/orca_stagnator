import requests

def test_validate_price_rounding_to_instrument_tick_size():
    base_url = "http://localhost:8000/api/v1/hedge/start"
    timeout = 30

    # Instruments and their expected tick sizes
    instruments_tick_sizes = {
        "ES": 0.25,
        "MES": 0.25,
        "NQ": 0.25,
        "MNQ": 0.25,
        "YM": 1.0,
        "MYM": 1.0,
        "RTY": 0.10,
        "M2K": 0.10,
    }

    # Sample accounts to test with (must be distinct)
    account_a_name = "TestAccountA"
    account_b_name = "TestAccountB"

    # Helper function to round a price according to tick size
    def round_price(price: float, tick_size: float) -> float:
        return round(round(price / tick_size) * tick_size, 8)

    # For testing, select representative test prices (choose odd decimals to check rounding)
    test_entry_price = 21000.13
    test_tp_distance = 5.37
    test_sl_distance = 3.68
    hedge_distance = 1.0

    # Test each instrument
    for instrument, tick_size in instruments_tick_sizes.items():
        # Calculate expected rounded prices
        entry_price_rounded = round_price(test_entry_price, tick_size)
        tp_distance_rounded = round_price(test_tp_distance, tick_size)
        sl_distance_rounded = round_price(test_sl_distance, tick_size)

        payload = {
            "account_a_name": account_a_name,
            "account_b_name": account_b_name,
            "instrument": instrument,
            "direction": "long",
            "entry_price": test_entry_price,
            "quantity": 1,
            "tp_distance": test_tp_distance,
            "sl_distance": test_sl_distance,
            "hedge_distance": hedge_distance,
        }

        try:
            response = requests.post(base_url, json=payload, timeout=timeout)
        except requests.RequestException as e:
            assert False, f"Request failed for instrument {instrument}: {e}"

        assert response.status_code == 200, f"Expected 200 OK but got {response.status_code} for instrument {instrument}"

        data = response.json()
        assert data.get("status") in ("success", "partial", "failed"), f"Unexpected status value for instrument {instrument}"

        acct_a = data.get("account_a_result")
        acct_b = data.get("account_b_result")
        assert acct_a is not None, f"Missing account_a_result for instrument {instrument}"
        assert acct_b is not None, f"Missing account_b_result for instrument {instrument}"

        # Validate account names match request
        assert acct_a.get("account_name") == account_a_name, f"Account A name mismatch for {instrument}"
        assert acct_b.get("account_name") == account_b_name, f"Account B name mismatch for {instrument}"

        # Validate rounding for Account A prices (entry_price, take_profit, stop_loss)
        # tp_distance and sl_distance are distances, but the response includes take_profit and stop_loss prices
        entry_price_a = acct_a.get("entry_price")
        take_profit_a = acct_a.get("take_profit")
        stop_loss_a = acct_a.get("stop_loss")

        # Account A entered long at entry_price, take_profit = entry_price + tp_distance, stop_loss = entry_price - sl_distance
        expected_tp_a = round_price(entry_price_rounded + tp_distance_rounded, tick_size)
        expected_sl_a = round_price(entry_price_rounded - sl_distance_rounded, tick_size)

        assert abs(entry_price_a - entry_price_rounded) < 1e-8, f"Account A entry_price not rounded correctly for {instrument}"
        assert abs(take_profit_a - expected_tp_a) < 1e-8, f"Account A take_profit not rounded correctly for {instrument}"
        assert abs(stop_loss_a - expected_sl_a) < 1e-8, f"Account A stop_loss not rounded correctly for {instrument}"

        # Validate rounding for Account B prices
        entry_price_b = acct_b.get("entry_price")
        take_profit_b = acct_b.get("take_profit")
        stop_loss_b = acct_b.get("stop_loss")

        # Account B direction is opposite (short), entry_price adjusted by hedge_distance:
        if payload["direction"].lower() == "long":
            expected_entry_b = round_price(entry_price_rounded + hedge_distance, tick_size)
            # For short: take_profit = entry_price - tp_distance, stop_loss = entry_price + sl_distance
            expected_tp_b = round_price(expected_entry_b - tp_distance_rounded, tick_size)
            expected_sl_b = round_price(expected_entry_b + sl_distance_rounded, tick_size)
        else:
            expected_entry_b = round_price(entry_price_rounded - hedge_distance, tick_size)
            expected_tp_b = round_price(expected_entry_b + tp_distance_rounded, tick_size)
            expected_sl_b = round_price(expected_entry_b - sl_distance_rounded, tick_size)

        assert abs(entry_price_b - expected_entry_b) < 1e-8, f"Account B entry_price not rounded correctly for {instrument}"
        assert abs(take_profit_b - expected_tp_b) < 1e-8, f"Account B take_profit not rounded correctly for {instrument}"
        assert abs(stop_loss_b - expected_sl_b) < 1e-8, f"Account B stop_loss not rounded correctly for {instrument}"

test_validate_price_rounding_to_instrument_tick_size()