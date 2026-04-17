from table import Table

class DatabaseManager:
    def __init__(self):
        self.databases = {}

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
