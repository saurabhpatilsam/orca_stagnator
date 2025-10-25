# 🏦 TRADOVATE ACCOUNTS SUMMARY REPORT

## Generated: 2025-10-21 20:11:40+01:00

---

## ✅ ACCOUNTS FROM TRADOVATE API (AUTHENTICATED)

Successfully authenticated with Tradovate using username/password credentials and fetched actual account data from the API.

### 📊 Summary Table

| Username     | Sub-Accounts | Account IDs |
|--------------|--------------|-------------|
| **APEX_272045** | 5 | PAAPEX2720450000001, PAAPEX2720450000002, PAAPEX2720450000003, PAAPEX2720450000004, PAAPEX2720450000005 |
| **APEX_136189** | 3 | PAAPEX1361890000010, PAAPEX1361890000011, APEX13618900000118 |
| **APEX_265995** | 1 | PAAPEX2659950000005 |
| **APEX_266668** | 4 | PAAPEX2666680000001, PAAPEX2666680000003, PAAPEX2666680000004, PAAPEX2666680000005 |

### 📈 Totals
- **Total APEX Usernames:** 4
- **Total Trading Accounts:** 13
- **All Accounts Active:** ✅ Yes (All Demo accounts)
- **Currency:** USD

---

## 🔑 ACCOUNTS IN REDIS

Data stored in Redis cache at: `orca-redis-manager.redis.cache.windows.net:6380`

### 📊 Summary Table

| Username     | Sub-Accounts | Account IDs |
|--------------|--------------|-------------|
| **APEX_136189** | 5 | PAAPEX1361890000007, PAAPEX1361890000002, PAAPEX1361890000008, PAAPEX1361890000009, PAAPEX1361890000010 |
| **APEX_265995** | 2 | PAAPEX2659950000001, PAAPEX2659950000002 |
| **APEX_266668** | 3 | PAAPEX2666680000001, PAAPEX2666680000002, PAAPEX2666680000003 |
| **APEX_272045** | 1 | PAAPEX2720450000001 |

### 📈 Totals
- **Total APEX Usernames:** 4
- **Total Trading Accounts in Redis:** 11
- **All Accounts Have Tokens:** ✅ Yes (TTL: ~45 minutes)

---

## 🔄 COMPARISON: TRADOVATE API vs REDIS

| Metric | Tradovate API | Redis | Status |
|--------|---------------|-------|--------|
| **Total Accounts** | 13 | 11 | ⚠️ Mismatch (+2 in Tradovate) |
| **APEX_272045** | 5 accounts | 1 account | ⚠️ 4 missing in Redis |
| **APEX_136189** | 3 accounts | 5 accounts | ⚠️ Different accounts |
| **APEX_265995** | 1 account | 2 accounts | ⚠️ 1 extra in Redis |
| **APEX_266668** | 4 accounts | 3 accounts | ⚠️ 1 missing in Redis |

### 🔍 Detailed Differences

#### APEX_272045
- **Tradovate:** 5 accounts (0001, 0002, 0003, 0004, 0005)
- **Redis:** 1 account (0001)
- **Missing in Redis:** PAAPEX2720450000002, PAAPEX2720450000003, PAAPEX2720450000004, PAAPEX2720450000005

#### APEX_136189
- **Tradovate:** PAAPEX1361890000010, PAAPEX1361890000011, APEX13618900000118
- **Redis:** PAAPEX1361890000007, PAAPEX1361890000002, PAAPEX1361890000008, PAAPEX1361890000009, PAAPEX1361890000010
- **Note:** Only PAAPEX1361890000010 is common between both

#### APEX_265995
- **Tradovate:** PAAPEX2659950000005
- **Redis:** PAAPEX2659950000001, PAAPEX2659950000002
- **Note:** Completely different accounts

#### APEX_266668
- **Tradovate:** PAAPEX2666680000001, PAAPEX2666680000003, PAAPEX2666680000004, PAAPEX2666680000005
- **Redis:** PAAPEX2666680000001, PAAPEX2666680000002, PAAPEX2666680000003
- **Missing in Redis:** PAAPEX2666680000004, PAAPEX2666680000005
- **Missing in Tradovate:** PAAPEX2666680000002

---

## 📋 COMPLETE ACCOUNT LIST FROM TRADOVATE API

### APEX_272045 (5 accounts)
1. **PAAPEX2720450000001** - Demo Account - ID: D17200370 - ✅ Active
2. **PAAPEX2720450000002** - Demo Account - ID: D17200423 - ✅ Active
3. **PAAPEX2720450000003** - Demo Account - ID: D17200474 - ✅ Active
4. **PAAPEX2720450000004** - Demo Account - ID: D17200522 - ✅ Active
5. **PAAPEX2720450000005** - Demo Account - ID: D18155916 - ✅ Active

### APEX_136189 (3 accounts)
1. **PAAPEX1361890000010** - Demo Account - ID: D18156785 - ✅ Active
2. **PAAPEX1361890000011** - Demo Account - ID: D30471976 - ✅ Active
3. **APEX13618900000118** - Demo Account - ID: D31104612 - ✅ Active

### APEX_265995 (1 account)
1. **PAAPEX2659950000005** - Demo Account - ID: D18156168 - ✅ Active

### APEX_266668 (4 accounts)
1. **PAAPEX2666680000001** - Demo Account - ID: D17158695 - ✅ Active
2. **PAAPEX2666680000003** - Demo Account - ID: D17159229 - ✅ Active
3. **PAAPEX2666680000004** - Demo Account - ID: D18155676 - ✅ Active
4. **PAAPEX2666680000005** - Demo Account - ID: D18155751 - ✅ Active

---

## 💡 RECOMMENDATIONS

1. **Update Redis Keys:** The Redis cache contains outdated or incorrect account IDs. Consider running the token generator to update Redis with the correct account list from Tradovate API.

2. **Sync Accounts:** There are 13 active accounts in Tradovate but only 11 in Redis. Update Redis to include all accounts.

3. **Token Management:** Ensure all 13 accounts from Tradovate have valid tokens stored in Redis for API operations.

4. **Verify APEX_136189:** This username has completely different accounts in Redis vs Tradovate. Investigate and update.

---

## 📁 Generated Files

- `redis_accounts.json` - Accounts found in Redis
- `tradovate_accounts.json` - Accounts fetched from Tradovate API
- `fetch_tradovate_accounts.py` - Script used to fetch accounts
- `get_all_accounts_from_redis.py` - Script used to query Redis

---

**Report Generated By:** ORCA Trading Platform  
**Data Source:** Tradovate Demo API (tv-demo.tradovateapi.com)  
**Redis Instance:** orca-redis-manager.redis.cache.windows.net:6380
