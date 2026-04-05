from table import Table
from WAL import WAL
from transaction import Transaction, recover   # ← only new import

class DatabaseManager:
    def __init__(self):
        self.databases = {}
        self.wal = WAL()               # ← one shared WAL for the whole manager
        self.active_txns = set()
        self.checkpoint_threshold = 100

    def create_database(self, db_name):
        if db_name in self.databases:
            print(f"Database '{db_name}' already exists.")
            return
        self.databases[db_name] = {}
        print(f"Database '{db_name}' created.")

    def delete_database(self, db_name):
        if db_name not in self.databases:
            print(f"Database '{db_name}' not found.")
            return
        del self.databases[db_name]
        print(f"Database '{db_name}' deleted.")

    def list_databases(self):
        if not self.databases:
            print("No databases exist.")
            return []
        print("Databases:", list(self.databases.keys()))
        return list(self.databases.keys())

    def create_table(self, db_name, table_name, schema, order=4, search_key=None):
        if db_name not in self.databases:
            print(f"Database '{db_name}' not found.")
            return
        if table_name in self.databases[db_name]:
            print(f"Table '{table_name}' already exists in '{db_name}'.")
            return
        self.databases[db_name][table_name] = Table(table_name, schema, order, search_key)
        print(f"Table '{table_name}' created in database '{db_name}'.")

    def delete_table(self, db_name, table_name):
        if db_name not in self.databases:
            print(f"Database '{db_name}' not found.")
            return
        if table_name not in self.databases[db_name]:
            print(f"Table '{table_name}' not found in '{db_name}'.")
            return
        del self.databases[db_name][table_name]
        print(f"Table '{table_name}' deleted from database '{db_name}'.")

    def list_tables(self, db_name):
        if db_name not in self.databases:
            print(f"Database '{db_name}' not found.")
            return []
        tables = list(self.databases[db_name].keys())
        print(f"Tables in '{db_name}':", tables)
        return tables

    def get_table(self, db_name, table_name):
        if db_name not in self.databases:
            print(f"Database '{db_name}' not found.")
            return None
        if table_name not in self.databases[db_name]:
            print(f"Table '{table_name}' not found in '{db_name}'.")
            return None
        return self.databases[db_name][table_name]

    # ── NEW: transaction support ─────────────────────────────────────────────
    def begin_transaction(self):
        """
        Create and return a new Transaction object tied to this DatabaseManager.
        The caller must call txn.begin() before performing any operations.
        """
        return Transaction(self, wal=self.wal)

    def register_transaction(self, txn_id):
        self.active_txns.add(txn_id)

    def unregister_transaction(self, txn_id):
        self.active_txns.discard(txn_id)

    def has_active_transactions(self):
        return bool(self.active_txns)

    def snapshot_state(self):
        snapshot = {}
        for db_name, tables in self.databases.items():
            snapshot[db_name] = {}
            for table_name, table in tables.items():
                snapshot[db_name][table_name] = [record for _, record in table.get_all()]
        return snapshot

    def checkpoint(self):
        if self.has_active_transactions():
            return None
        snapshot = self.snapshot_state()
        return self.wal.log_checkpoint(snapshot)

    def maybe_checkpoint(self):
        if self.has_active_transactions():
            return None
        entries = self.wal.read_all()
        if len(entries) < self.checkpoint_threshold:
            return None
        return self.checkpoint()

    # ── NEW: crash recovery ──────────────────────────────────────────────────
    def recover(self):
        """
        Read the WAL file and undo any transactions that never committed.
        Call this once on startup before doing any other operations.
        """
        return recover(self, wal=self.wal)
