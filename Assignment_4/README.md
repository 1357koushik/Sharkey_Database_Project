# Sports Club Database - Assignment 4: Sharding

A horizontal scaling solution for the Sports Club Management database using hash-based sharding across multiple SQLite databases.

---

##  Project Overview

This project extends a member-centric Sports Club database with **horizontal sharding** to demonstrate scalable database design principles. Data is distributed across 3 shards using Member_ID as the shard key, with a Flask REST API for shard-aware queries.

### Sharding Strategy

| Property | Value |
|----------|-------|
| **Shard Key** | `Member_ID` (e.g., M01–M40) |
| **Strategy** | Hash-based: `shard_id = int(member_id[1:]) % 3` |
| **Number of Shards** | 3 independent SQLite databases |
| **Distribution** | ~14 members per shard (40 members ÷ 3 shards) |
| **Query Pattern** | Lookup (single shard) & Range/Scatter-Gather (all shards) |

---

##  Project Structure

```
Assignment_4/
├── sharded_app.py              # Flask API server (port 5001)
├── router/
│   ├── shard_config.py        # Shard topology & routing logic
│   ├── query_router.py        # Shard-aware query functions
│   ├── init_shards.py         # Database initialization script
│   └── migrate_data.py        # Data migration to shards
├── shards/
│   ├── shard_0.db            # Shard 0 database
│   ├── shard_1.db            # Shard 1 database
│   └── shard_2.db            # Shard 2 database
├── sports_club.db            # Source database (pre-sharding)
├── tests/                     # Test suite
├── CS432_Assignment4_Report.ipynb  # Detailed analysis & documentation
└── README.md                  # This file
```

---

##  Sharded Tables

**Member-Centric Tables** (distributed across shards):

| Table | Rows | Shard Key | Purpose |
|-------|------|-----------|---------|
| Member | 40 | Member_ID | Member profiles |
| Player | 20 | Member_ID | Player information |
| Coach | 20 | Member_ID | Coach details |
| Administrator | 10 | Member_ID | Admin staff |
| Booking | 20 | Member_ID | Facility bookings |
| Attendance | 20 | Member_ID | Event attendance |
| Equipment_Loan | 20 | Member_ID | Equipment loans |
| Complaint | 20 | Raised_By (Member_ID) | Member complaints |
| Player_Stat | 20 | Member_ID | Player statistics |
| Team_Roster | 20 | Member_ID (via Player) | Team assignments |

**Reference Tables** (replicated to every shard):
- Sport, Facility, Equipment, Team, Event

---

##  Quick Start

### Prerequisites
- Python 3.8+
- Flask (`pip install flask`)
- SQLite3 (built-in)

### Installation & Setup

```bash
# Install dependencies
pip install flask

# Initialize shards (creates shard_0.db, shard_1.db, shard_2.db)
python3 router/init_shards.py

# Migrate data from source to shards
python3 router/migrate_data.py
```

### Running the Server

```bash
# Start the Flask API server (listens on http://localhost:5001)
python3 sharded_app.py
```

The server will start in debug mode on port 5001.

---

##  API Endpoints

### Lookup Queries (Single Shard)

**Get Member Details**
```
GET /shards/members/<member_id>
```
Response includes shard routing metadata:
```json
{
  "Member_ID": "M01",
  "Name": "Alice Johnson",
  "Age": 28,
  "_routing": {
    "shard_id": 1,
    "shard_db": "shard_1.db",
    "routing_formula": "int('01') % 3 = 1"
  }
}
```

**Get Member Bookings**
```
GET /shards/members/<member_id>/bookings
```

**Get Member Complaints**
```
GET /shards/members/<member_id>/complaints
```

**Get Member Stats**
```
GET /shards/members/<member_id>/stats
```

### Insert Mutations (Routed to Correct Shard)

**Create Member**
```
POST /shards/members
Content-Type: application/json

{
  "Member_ID": "M41",
  "Name": "Bob Smith",
  "Age": 25,
  "Phone": "555-0123"
}
```

**Create Booking**
```
POST /shards/bookings
Content-Type: application/json

{
  "Member_ID": "M01",
  "Booking_Date": "2026-02-15",
  "Facility_ID": "F001",
  "Start_Time": "18:00",
  "End_Time": "19:00"
}
```

**Record Attendance**
```
POST /shards/attendance
Content-Type: application/json

{
  "Member_ID": "M01",
  "Event_ID": "E001",
  "Attendance_Date": "2026-02-15"
}
```

### Range & Scatter-Gather Queries (All Shards)

**List All Members (or filter by age)**
```
GET /shards/members?age_min=20&age_max=35
```

**Find Bookings by Date Range**
```
GET /shards/bookings?date_start=2026-01-01&date_end=2026-12-31
```

**Find Attendance by Date Range**
```
GET /shards/attendance?date_start=2026-01-01&date_end=2026-12-31
```

### Diagnostics

**View Shard Topology**
```
GET /shards/info
```
Returns shard configuration and member distribution across shards.

---

##  Routing Logic

### Shard Selection Formula

```python
def get_shard_id(member_id: str) -> int:
    numeric = int(member_id[1:])   # Extract numeric suffix: "M01" → 1
    return numeric % NUM_SHARDS     # Hash to shard: 1 % 3 = 1
```

### Member Distribution Example

- Shard 0: M03, M06, M09, M12, M15, ... (14 members)
- Shard 1: M01, M04, M07, M10, M13, ... (13 members)
- Shard 2: M02, M05, M08, M11, M14, ... (13 members)

*Maximum skew: ±1 row (<4%)*

---

##  Testing

Run the test suite:
```bash
python3 -m pytest tests/ -v
```

Key test scenarios:
-  Single-shard lookup queries
-  Multi-shard range/scatter-gather queries
-  Shard-aware insert/mutation operations
-  Routing correctness for all 40 members
-  Data consistency across shards
-  Reference table replication

---

##  Key Files

### `shard_config.py`
Central configuration module defining:
- Shard topology (3 shards)
- Routing algorithm
- Shard database paths
- Helper functions for shard lookup

### `query_router.py`
Shard-aware query layer implementing:
- `get_member()` - Single shard lookup
- `range_members_by_age()` - Multi-shard range query
- `insert_member()` - Route insert to correct shard
- Scatter-gather operations

### `sharded_app.py`
Flask REST API server with endpoints for:
- Lookup queries (routed to single shard)
- Mutations (routed to correct shard)
- Range queries (scatter-gather from all shards)
- Diagnostics (shard topology info)

### `init_shards.py`
Database initialization:
- Creates schema in each shard
- Loads reference data to all shards
- Verifies shard readiness

### `migrate_data.py`
Data migration:
- Reads source database
- Partitions member-centric data by shard
- Writes to corresponding shard databases

---

##  Performance Considerations

| Operation | Shards Touched | Complexity | Notes |
|-----------|----------------|-----------|-------|
| Get Member by ID | 1 | O(1) routing + O(log n) lookup | Fast; deterministic shard selection |
| Insert Member | 1 | O(1) routing + O(1) insert | Fast; single shard write |
| Range by Age | All 3 | O(3) routing + O(n) scan | Slower; must scan all shards |
| Range by Date | All 3 | O(3) routing + O(n) scan | Slower; must scan all shards |

---

##  Data Integrity

- **Foreign Keys**: Enabled (`PRAGMA foreign_keys = ON`)
- **Referential Integrity**: Reference tables replicated to all shards
- **Consistency**: Each shard is independent SQLite database with full ACID guarantees
- **Cross-Shard Joins**: Not supported (data distributed by design)

---
