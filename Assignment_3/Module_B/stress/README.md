# Locust Stress Testing

This folder contains a real [Locust](https://locust.io/) load test for the Module B web server.

## What it tests

- `GET /api/tables`
- `GET /api/wal`
- `GET /api/acid/recover`
- `POST /api/acid/stress` for race-condition correctness
- `POST /api/stress/load` for high-volume stress testing

## Setup

From `Module_B`:

```bash
pip install -r requirements.txt
```

## Start the app

From `Module_B/web`:

```bash
python app.py
```

The Flask app should be available at `http://localhost:5001`.

## Run Locust UI

From `Module_B/stress`:

```bash
locust -f locustfile.py --host http://localhost:5001
```

Then open the Locust web UI, usually at `http://localhost:8089`.

Suggested first run:

- Users: `50`
- Spawn rate: `10`

## Run headless

Example:

```bash
locust -f locustfile.py --host http://localhost:5001 --headless -u 100 -r 20 -t 2m
```

This means:

- `-u 100`: 100 concurrent users
- `-r 20`: spawn 20 users per second
- `-t 2m`: run for 2 minutes

## Notes

- The race-condition task checks final stock and order-count correctness.
- The stress-load task checks that all internally generated requests completed successfully.
- You can increase users gradually to hundreds or thousands depending on your machine.
