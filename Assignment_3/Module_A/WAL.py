import json
import os
import threading

WAL_FILE = "wal.log"


class WAL:
    def __init__(self, filepath=WAL_FILE):
        self.filepath = filepath
        self._lock = threading.Lock()

    def _ensure_parent_dir(self):
        parent = os.path.dirname(os.path.abspath(self.filepath))
        if parent:
            os.makedirs(parent, exist_ok=True)

    def _write(self, entry):
        with self._lock:
            self._ensure_parent_dir()
            with open(self.filepath, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
                f.flush()
                os.fsync(f.fileno())

    def log_begin(self, txn_id):
        self._write({"txn_id": txn_id, "op": "BEGIN"})

    def log_insert(self, txn_id, db_name, table_name, key, value):
        self._write({
            "txn_id": txn_id,
            "op": "INSERT",
            "db": db_name,
            "table": table_name,
            "key": key,
            "value": value,
        })

    def log_update(self, txn_id, db_name, table_name, key, old_value, new_value):
        self._write({
            "txn_id": txn_id,
            "op": "UPDATE",
            "db": db_name,
            "table": table_name,
            "key": key,
            "old_value": old_value,
            "new_value": new_value,
        })

    def log_delete(self, txn_id, db_name, table_name, key, old_value):
        self._write({
            "txn_id": txn_id,
            "op": "DELETE",
            "db": db_name,
            "table": table_name,
            "key": key,
            "old_value": old_value,
        })

    def log_commit(self, txn_id):
        self._write({"txn_id": txn_id, "op": "COMMIT"})

    def log_rollback(self, txn_id):
        self._write({"txn_id": txn_id, "op": "ROLLBACK"})

    def log_checkpoint(self, snapshot):
        checkpoint = {"txn_id": "SYSTEM", "op": "CHECKPOINT", "snapshot": snapshot}
        with self._lock:
            self._ensure_parent_dir()
            with open(self.filepath, "w", encoding="utf-8") as f:
                f.write(json.dumps(checkpoint) + "\n")
                f.flush()
                os.fsync(f.fileno())
        return checkpoint

    def read_all(self):
        if not os.path.exists(self.filepath):
            return []
        entries = []
        with open(self.filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries

    def clear(self):
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
