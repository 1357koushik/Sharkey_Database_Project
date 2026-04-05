# Mini Database Engine (B+ Tree + Transactions + WAL)

## Overview

This project implements a **lightweight in-memory database system** with:

- **B+ Tree indexing** for efficient data storage and retrieval  
- **Table abstraction** with schema validation  
- **Transaction system** with:
  - Write-Ahead Logging (WAL)
  - Undo logging
  - Basic locking for isolation  
- **Crash recovery** using WAL  

The system simulates core database internals: indexing, transactions, durability, and recovery.

---

## Architecture

### 1. Storage Layer — B+ Tree
Implemented in: :contentReference[oaicite:0]{index=0}

- Balanced tree structure
- Leaf nodes store actual records
- Internal nodes store routing keys
- Linked leaf nodes for range queries

**Supported operations:**
- Insert
- Search
- Update
- Delete
- Range Query
- Full Scan

---

### 2. Table Layer
Implemented in: :contentReference[oaicite:1]{index=1}

Acts as an abstraction over the B+ Tree.

**Responsibilities:**
- Schema validation (type checking)
- Enforcing presence of search key
- Mapping records → keys

**Operations:**
- `insert(record)`
- `update(key, record)`
- `delete(key)`
- `get(key)`
- `get_all()`
- `range_query(start, end)`

---

### 3. Database Manager
Implemented in: :contentReference[oaicite:2]{index=2}

Top-level controller.

**Responsibilities:**
- Manage multiple databases
- Manage tables inside each database
- Provide transaction interface
- Manage shared WAL

**Operations:**
- Create/Delete database
- Create/Delete table
- List databases/tables
- Start transaction
- Run recovery

---

### 4. Transaction System
Implemented in: :contentReference[oaicite:3]{index=3}

Provides **ACID-like behavior (partial)**.

#### Features

**1. Write-Ahead Logging (WAL)**
- Every operation is logged before execution

**2. Undo Logging**
- Stores previous state for rollback

**3. Locking**
- Per-table `RLock`
- Prevents concurrent conflicts

**Transaction Flow**