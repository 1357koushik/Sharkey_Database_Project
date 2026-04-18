# Assignment 4 — Distributed Sharding (Team 38: Sharkey)

Assignment 4 runtime now uses the **assigned distributed MySQL shards** for all shard storage and routing logic.

## Runtime backend

- 3 shard instances (`shard_index` 0,1,2)
- Shard key: `Member_ID`
- Routing: `int(member_id[1:]) % 3`
- Storage engine: MySQL (`10.0.116.184` ports `3307`, `3308`, `3309`)
- Team DB/User: `Sharkey`

## Install

```bash
py -m pip install -r requirements.txt
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
