
# TestSprite AI Testing Report(MCP)

---

## 1️⃣ Document Metadata
- **Project Name:** orca-ven-backend-main
- **Date:** 2025-10-25
- **Prepared by:** TestSprite AI Team

---

## 2️⃣ Requirement Validation Summary

#### Test TC001
- **Test Name:** validate_hedge_start_accepts_account_a_alias
- **Test Code:** [TC001_validate_hedge_start_accepts_account_a_alias.py](./TC001_validate_hedge_start_accepts_account_a_alias.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 58, in <module>
  File "<string>", line 35, in test_validate_hedge_start_accepts_account_a_alias
AssertionError: Expected 200 OK for account_a_name alias, got 503

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/438a93da-61b6-417f-96df-03acf219046d/eea78ce5-e04b-4bf5-8a32-6a51568983fa
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC002
- **Test Name:** validate_hedge_start_input_validation
- **Test Code:** [TC002_validate_hedge_start_input_validation.py](./TC002_validate_hedge_start_input_validation.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 154, in <module>
  File "<string>", line 152, in validate_hedge_start_input_validation
AssertionError: Test case #5 expected 200 but got 503. Payload: {'account_a_name': 'AccountA1', 'account_b_name': 'AccountB5', 'instrument': 'MNQ', 'direction': 'long', 'entry_price': 21000.25, 'quantity': 1, 'tp_distance': 0, 'sl_distance': 2, 'hedge_distance': 1}

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/438a93da-61b6-417f-96df-03acf219046d/c71fa8fa-95de-468d-8479-6ff475a29a39
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC003
- **Test Name:** validate_concurrent_order_placement_on_hedge_start
- **Test Code:** [TC003_validate_concurrent_order_placement_on_hedge_start.py](./TC003_validate_concurrent_order_placement_on_hedge_start.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 79, in <module>
  File "<string>", line 33, in validate_concurrent_order_placement_on_hedge_start
AssertionError: Expected status 200 OK but got 503

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/438a93da-61b6-417f-96df-03acf219046d/e78d19aa-618d-4446-abc7-cabadf7068c8
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC004
- **Test Name:** validate_price_rounding_to_instrument_tick_size
- **Test Code:** [TC004_validate_price_rounding_to_instrument_tick_size.py](./TC004_validate_price_rounding_to_instrument_tick_size.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 105, in <module>
  File "<string>", line 57, in test_validate_price_rounding_to_instrument_tick_size
AssertionError: Expected 200 OK but got 400 for instrument ES

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/438a93da-61b6-417f-96df-03acf219046d/1628dfc0-7855-4eee-89d2-a9befaa7f1ed
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC005
- **Test Name:** validate_trading_accounts_api_cache_support
- **Test Code:** [TC005_validate_trading_accounts_api_cache_support.py](./TC005_validate_trading_accounts_api_cache_support.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/438a93da-61b6-417f-96df-03acf219046d/ccc451cd-be90-430b-a0d2-0b8a9530026f
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC006
- **Test Name:** validate_positions_api_minimal_latency_response
- **Test Code:** [TC006_validate_positions_api_minimal_latency_response.py](./TC006_validate_positions_api_minimal_latency_response.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 64, in <module>
  File "<string>", line 62, in test_validate_positions_api_minimal_latency_response
AssertionError: Positions API response latency too high: 1.335 seconds

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/438a93da-61b6-417f-96df-03acf219046d/62c3c539-6c6e-4a28-9703-fb4fda0205d9
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC007
- **Test Name:** validate_pending_orders_api_response
- **Test Code:** [TC007_validate_pending_orders_api_response.py](./TC007_validate_pending_orders_api_response.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/438a93da-61b6-417f-96df-03acf219046d/47aeb3c9-37dd-4cf9-9040-7e35db1038a4
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC008
- **Test Name:** validate_account_balances_api_response
- **Test Code:** [TC008_validate_account_balances_api_response.py](./TC008_validate_account_balances_api_response.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/438a93da-61b6-417f-96df-03acf219046d/ad99d9ac-65f3-4d1c-94bd-b2762784e837
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC009
- **Test Name:** validate_health_check_api_response
- **Test Code:** [TC009_validate_health_check_api_response.py](./TC009_validate_health_check_api_response.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/438a93da-61b6-417f-96df-03acf219046d/6bb851b6-8f59-452f-9cc5-c232b82798ea
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---


## 3️⃣ Coverage & Matching Metrics

- **44.44** of tests passed

| Requirement        | Total Tests | ✅ Passed | ❌ Failed  |
|--------------------|-------------|-----------|------------|
| ...                | ...         | ...       | ...        |
---


## 4️⃣ Key Gaps / Risks
{AI_GNERATED_KET_GAPS_AND_RISKS}
---