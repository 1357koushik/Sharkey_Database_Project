# Module B — Concurrent Workload & Stress Testing
## CS432 Assignment 3 · IIT Gandhinagar

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the web server
cd Module_B/web
python3 app.py
# Open → http://localhost:5001

# 3. Run Locust stress tests (separate terminal)
cd Module_B/stress
locust -f locustfile.py --host http://localhost:5001
```

---

## What's In This Folder

```
Module_B/
├── web/
│   ├── app.py               Flask server — all ACID demo endpoints   ← NEW
│   ├── database.py          3 B+ Tree tables + seed data              ← NEW
│   ├── templates/
│   │   └── index.html       Full dark-theme single-page app           ← NEW
│   └── static/
│       ├── css/style.css    UI styling                                ← NEW
│       └── js/
│           ├── api.js       Fetch wrappers for all endpoints          ← NEW
│           └── app.js       SPA router + all view renderers           ← NEW
├── stress/
│   ├── locustfile.py        Locust load-test suite                    ← NEW
│   └── README.md            Locust run instructions                   ← NEW
├── logs/
│   └── wal.log              Written by web server
└── requirements.txt         flask only
```

> Engine is imported from `../Module_A/engine/` — no duplication.

---

## Web UI (http://localhost:5001)

| Page | What It Shows |
|---|---|
| Dashboard | Live view of all 3 B+ Tree tables |
| Atomicity | Crash demo with step-by-step trace + before/after state |
| Consistency | Constraint violation — negative balance blocked |
| Isolation | Two concurrent threads, execution log, dirty-read check |
| Durability | Wipe B+ Tree → WAL recovery → record reappears |
| 3-Table Txn | Atomic commit or injected failure across all 3 tables |
| Manual Txn | BUILD your own: BEGIN → INSERT/UPDATE/DELETE → COMMIT/ROLLBACK |
| WAL Log | Every log record with op badges and before/after images |
| Recovery | Trigger ARIES recovery manually |
| Race Condition | Concurrent booking correctness test |
| Stress Test | Browser-based load test with latency histogram |

---

## API Endpoints (Total 17 endpoints)

| Method | Path | Description |
|---|---|---|
| GET | `/` | Web UI |
| GET | `/api/tables` | All table contents |
| GET | `/api/wal` | WAL summary + last 50 records |
| POST | `/api/txn/begin` | Start transaction |
| POST | `/api/txn/commit` | Commit `{txn_id}` |
| POST | `/api/txn/rollback` | Rollback `{txn_id}` |
| POST | `/api/txn/insert` | Insert `{txn_id, table, record}` |
| POST | `/api/txn/update` | Update `{txn_id, table, key, record}` |
| POST | `/api/txn/delete` | Delete `{txn_id, table, key}` |
| POST | `/api/acid/atomicity` | Run Atomicity demo |
| POST | `/api/acid/consistency` | Run Consistency demo |
| POST | `/api/acid/isolation` | Run Isolation demo |
| POST | `/api/acid/durability` | Run Durability demo |
| POST | `/api/acid/multi` | 3-table transaction `{user_id, product_id, inject_fail}` |
| POST | `/api/acid/stress` | Race condition correctness test |
| POST | `/api/stress/load` | High-volume stress/load test |
| GET | `/api/acid/recover` | Trigger ARIES recovery |

---

## Stress Test Results (12 threads)

| Test | Config | Result |
|---|---|---|
| Race Condition | 12 threads → 1 product | `stock_delta == committed_txns` |
| Concurrent 3-Table ACID | 12 threads | All commit or rollback cleanly |
| Load Test | 12T × 30R = 360 ops | 0% error rate |
| Failure Simulation | 20 crash trials | 20/20 clean rollbacks (100%) |
