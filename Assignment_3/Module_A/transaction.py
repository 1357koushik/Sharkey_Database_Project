import threading
from WAL import WAL

# ── module-level per-table locks (shared across all Transaction objects) ─────
# Key  : "db_name.table_name"
# Value: threading.RLock()
# A transaction acquires all locks it needs on begin and releases on commit/rollback.
_TABLE_LOCKS: dict = {}
_LOCKS_MUTEX = threading.Lock()   # protects creation of new lock entries


def _resolve_db_name(db_manager, db_name):
    if db_name is not None:
        return db_name
    names = list(getattr(db_manager, "databases", {}).keys())
    return names[0] if len(names) == 1 else db_name


def _safe_get_table(db_manager, db_name, table_name):
    if db_name is None:
        return None
    databases = getattr(db_manager, "databases", {})
    return databases.get(db_name, {}).get(table_name)


def _apply_checkpoint_snapshot(db_manager, snapshot):
    for db_name, tables in snapshot.items():
        database = getattr(db_manager, "databases", {}).get(db_name)
        if database is None:
            continue
        for table_name, records in tables.items():
            table = database.get(table_name)
            if table is None:
                continue
            for key, _ in list(table.get_all()):
                table._raw_delete(key)
            for record in records:
                key = record.get(table.search_key)
                if key is not None:
                    table._raw_insert(key, record)


def _get_lock(db_name, table_name):
    """Return (creating if necessary) the RLock for a specific table."""
    lock_key = f"{db_name}.{table_name}"
    with _LOCKS_MUTEX:
        if lock_key not in _TABLE_LOCKS:
            _TABLE_LOCKS[lock_key] = threading.RLock()
        return _TABLE_LOCKS[lock_key]


class Transaction:
    """
    Transaction — BEGIN / COMMIT / ROLLBACK
    ────────────────────────────────────────
    Wraps your existing Table methods with:
      1. Write-Ahead Logging  — every op is logged to WAL before touching B+ Tree
      2. In-memory undo log   — stores old values so rollback can reverse each step
      3. Per-table locking    — acquires a lock on each table touched (released on
                                commit/rollback) for basic isolation

    Usage:
        txn = db.begin_transaction()
        txn.begin()
        txn.insert("university", "users",   record)
        txn.update("university", "products", key, new_record)
        txn.delete("university", "orders",  key)
        txn.commit()          # or txn.rollback()
    """

    _id_counter = 0
    _id_lock    = threading.Lock()

    def __init__(self, db_manager, wal=None):
        self.db       = db_manager
        self.wal      = wal or WAL()
        self.undo_log = []      # list of (op, db_name, table_name, key, old_value)
        self.active   = False
        self.txn_id   = None
        self._held_locks = []   # list of RLock objects we currently hold

    # ── generate a unique transaction id ────────────────────────────────────
    @classmethod
    def _new_id(cls):
        with cls._id_lock:
            cls._id_counter += 1
            return f"T{cls._id_counter}"

    # ── guard: raise if no active transaction ────────────────────────────────
    def _check_active(self):
        if not self.active:
            raise RuntimeError("No active transaction — call begin() first.")

    # ── acquire a table lock (for isolation) ────────────────────────────────
    def _acquire(self, db_name, table_name):
        lock = _get_lock(db_name, table_name)
        lock.acquire()               # blocks if another transaction holds it
        self._held_locks.append(lock)

    # ── release all held locks ───────────────────────────────────────────────
    def _release_all(self):
        for lock in self._held_locks:
            try:
                lock.release()
            except RuntimeError:
                pass   # already released
        self._held_locks.clear()

    
    # PUBLIC API
    

    def begin(self):
        """Start the transaction — log BEGIN to WAL, reset undo log."""
        if self.active:
            raise RuntimeError("Transaction already active.")
        self.txn_id   = self._new_id()
        self.undo_log = []
        self.active   = True
        if hasattr(self.db, "register_transaction"):
            self.db.register_transaction(self.txn_id)
        self.wal.log_begin(self.txn_id)
        print(f"[TXN {self.txn_id}] BEGIN")

    # ── INSERT ────
    def insert(self, db_name, table_name, record):
        """
        Log INSERT → acquire table lock → insert into B+ Tree → record undo info.
        To undo an insert: delete the key that was inserted.
        """
        self._check_active()
        table = self.db.get_table(db_name, table_name)
        if table is None:
            raise ValueError(f"Table '{table_name}' not found in '{db_name}'.")

        key = record.get(table.search_key)
        if key is None:
            raise ValueError(f"Search key '{table.search_key}' missing in record.")

        self._acquire(db_name, table_name)          # isolation lock

        # 1. Write-Ahead: log BEFORE touching B+ Tree
        self.wal.log_insert(self.txn_id, db_name, table_name, key, record)

        # 2. Perform the actual operation on the B+ Tree
        table.insert(record)

        # 3. Store undo info (old_value=None because nothing existed before)
        self.undo_log.append(("INSERT", db_name, table_name, key, None))
        print(f"  [{self.txn_id}] INSERT -> {table_name}, key={key}")

    # ── UPDATE ───────────────────────────────────────────────────────────────
    def update(self, db_name, table_name, key, new_record):
        """
        Capture old value → Log UPDATE → acquire lock → update B+ Tree → record undo.
        To undo an update: restore the old value.
        """
        self._check_active()
        table = self.db.get_table(db_name, table_name)
        if table is None:
            raise ValueError(f"Table '{table_name}' not found in '{db_name}'.")

        # Capture old value BEFORE any change (needed for undo)
        old_value = table.get(key)
        if old_value is None:
            raise ValueError(f"Key {key} not found in '{table_name}'.")

        self._acquire(db_name, table_name)          # isolation lock

        # 1. Write-Ahead
        self.wal.log_update(self.txn_id, db_name, table_name, key, old_value, new_record)

        # 2. Perform operation
        table.update(key, new_record)

        # 3. Undo info: restore old_value
        self.undo_log.append(("UPDATE", db_name, table_name, key, old_value))
        print(f"  [{self.txn_id}] UPDATE -> {table_name}, key={key}")

    # ── DELETE ────────
    def delete(self, db_name, table_name, key):
        """
        Capture old value → Log DELETE → acquire lock → delete from B+ Tree → record undo.
        To undo a delete: re-insert the old value.
        """
        self._check_active()
        table = self.db.get_table(db_name, table_name)
        if table is None:
            raise ValueError(f"Table '{table_name}' not found in '{db_name}'.")

        # Capture old value before deleting
        old_value = table.get(key)
        if old_value is None:
            raise ValueError(f"Key {key} not found in '{table_name}'.")

        self._acquire(db_name, table_name)          # isolation lock

        # 1. Write-Ahead
        self.wal.log_delete(self.txn_id, db_name, table_name, key, old_value)

        # 2. Perform operation
        table.delete(key)

        # 3. Undo info: re-insert old_value
        self.undo_log.append(("DELETE", db_name, table_name, key, old_value))
        print(f"  [{self.txn_id}] DELETE -> {table_name}, key={key}")

    # ── COMMIT ──
    def commit(self):
        """
        Write COMMIT to WAL → clear undo log → release locks.
        Once COMMIT is in the WAL file, data is durable even after a crash.
        """
        self._check_active()
        self.wal.log_commit(self.txn_id)   # durability: COMMIT written to disk first
        self.undo_log = []
        self.active   = False
        if hasattr(self.db, "unregister_transaction"):
            self.db.unregister_transaction(self.txn_id)
        self._release_all()
        if hasattr(self.db, "maybe_checkpoint"):
            self.db.maybe_checkpoint()
        print(f"[TXN {self.txn_id}] COMMIT")

    # ── ROLLBACK ─────
    def rollback(self):
        """
        Undo all operations in REVERSE order → log ROLLBACK → release locks.
        Each undo step applies the inverse operation directly to the B+ Tree.
        """
        self._check_active()
        print(f"[TXN {self.txn_id}] ROLLBACK — undoing {len(self.undo_log)} operation(s)...")

        # Undo in REVERSE order (last op undone first)
        for op, db_name, table_name, key, old_value in reversed(self.undo_log):
            table = self.db.get_table(db_name, table_name)
            if op == "INSERT":
                table.delete(key)                  # undo insert  → delete
                print(f"  Undid INSERT: deleted key={key} from {table_name}")
            elif op == "UPDATE":
                table.update(key, old_value)       # undo update  → restore old
                print(f"  Undid UPDATE: restored key={key} in {table_name}")
            elif op == "DELETE":
                table.insert(old_value)            # undo delete  → re-insert
                print(f"  Undid DELETE: re-inserted key={key} in {table_name}")

        self.wal.log_rollback(self.txn_id)
        self.undo_log = []
        self.active   = False
        if hasattr(self.db, "unregister_transaction"):
            self.db.unregister_transaction(self.txn_id)
        self._release_all()
        print(f"[TXN {self.txn_id}] ROLLBACK complete ✓")



# CRASH RECOVERY


def recover(db_manager, wal=None):
    """
    Called on system startup — reads the WAL file and:
      • Transactions with COMMIT -> REDO them so committed data survives restart
      • Transactions without COMMIT -> UNDO them so partial writes disappear
    """
    wal = wal or WAL()
    entries = wal.read_all()

    if not entries:
        print("[RECOVERY] WAL is empty — nothing to recover.")
        return {"status": "clean", "records": 0, "committed": [], "undone": [], "checkpoint": False}

    checkpoint_entry = None
    checkpoint_index = -1
    for idx, entry in enumerate(entries):
        if entry.get("op") == "CHECKPOINT":
            checkpoint_entry = entry
            checkpoint_index = idx

    if checkpoint_entry is not None:
        _apply_checkpoint_snapshot(db_manager, checkpoint_entry.get("snapshot", {}))
        entries = entries[checkpoint_index + 1:]
        print("[RECOVERY] Restored latest CHECKPOINT snapshot.")

    # ── Group log entries by transaction id ──────────────────────────────────
    txns = {}
    for entry in entries:
        if entry.get("op") == "CHECKPOINT":
            continue
        tid = entry["txn_id"]
        if tid not in txns:
            txns[tid] = {"ops": [], "committed": False, "rolled_back": False}
        if entry["op"] == "COMMIT":
            txns[tid]["committed"] = True
        elif entry["op"] == "ROLLBACK":
            txns[tid]["rolled_back"] = True
        elif entry["op"] not in ("BEGIN", "ROLLBACK"):
            txns[tid]["ops"].append(entry)

    committed_ids = sorted(tid for tid, data in txns.items() if data["committed"])
    loser_ids = sorted(
        tid for tid, data in txns.items()
        if not data["committed"] and not data["rolled_back"]
    )

    for tid in committed_ids:
        print(f"[RECOVERY] {tid} — COMMITTED, redoing {len(txns[tid]['ops'])} op(s)...")
        for entry in txns[tid]["ops"]:
            op = entry["op"]
            db_name = _resolve_db_name(db_manager, entry.get("db"))
            table_name = entry.get("table")
            key = entry.get("key")
            table = _safe_get_table(db_manager, db_name, table_name)
            if table is None:
                continue
            try:
                if op == "INSERT":
                    value = entry.get("value")
                    if value is not None and table.get(key) is None:
                        table.insert(value)
                elif op == "UPDATE":
                    new_value = entry.get("new_value")
                    if new_value is not None and table.get(key) is not None:
                        table.update(key, new_value)
                elif op == "DELETE":
                    if table.get(key) is not None:
                        table.delete(key)
            except Exception:
                pass
        print(f"[RECOVERY] {tid} — Redo complete ✓")

    for tid in loser_ids:
        txn_data = txns[tid]
        print(f"[RECOVERY] {tid} — NO COMMIT found, undoing {len(txn_data['ops'])} op(s)...")
        for entry in reversed(txn_data["ops"]):
            op = entry["op"]
            db_name = _resolve_db_name(db_manager, entry.get("db"))
            table_name = entry.get("table")
            key = entry.get("key")
            table = _safe_get_table(db_manager, db_name, table_name)
            if table is None:
                continue
            if op == "INSERT":
                if table.get(key) is not None:
                    table.delete(key)
                print(f"  Recovery: deleted inserted key={key} from {table_name}")
            elif op == "UPDATE":
                old_val = entry.get("old_value")
                if old_val is not None:
                    table.update(key, old_val)
                print(f"  Recovery: restored key={key} in {table_name}")
            elif op == "DELETE":
                old_val = entry.get("old_value")
                if old_val is not None:
                    table.insert(old_val)
                print(f"  Recovery: re-inserted key={key} in {table_name}")
        wal.log_rollback(tid)
        print(f"[RECOVERY] {tid} — Undo complete ✓")

    return {
        "status": "recovered" if txns or checkpoint_entry is not None else "clean",
        "records": len(entries),
        "committed": committed_ids,
        "undone": loser_ids,
        "checkpoint": checkpoint_entry is not None,
    }
