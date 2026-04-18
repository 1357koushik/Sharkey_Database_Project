# Assignment 4 — Distributed Sharding (Team 38: Sharkey)

Assignment 4 runtime now uses the **Assignment 3 database engine** (B+Tree + WAL) for all shard storage and routing logic.

## Runtime backend

- 3 shard instances (`shard_index` 0,1,2)
- Shard key: `Member_ID`
- Routing: `int(member_id[1:]) % 3`
- Storage engine: Assignment 3 `DatabaseManager` / `Table`

## Install

```bash
py -m pip install flask
```

## Run

```bash
python router\init_shards.py
python router\migrate_data.py
python sharded_app.py
```

## Verify

```bash
python tests\verify_sharding.py
```
