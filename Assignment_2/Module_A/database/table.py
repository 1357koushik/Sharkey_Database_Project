from bplustree import bplustree

class Table:
    def __init__(self, name, schema, order=4, search_key=None):
        self.name = name
        self.schema = schema
        self.order = order
        self.data = bplustree(order)
        self.search_key = search_key

    def validate_record(self, record):
        
        for col in self.schema:
            if col not in record:
                print(f"Missing column '{col}' in record.")
                return False
        
        type_map = {"int": int, "str": str, "float": float, "bool": bool}
        for col, dtype in self.schema.items():
            expected_type = type_map.get(dtype)
            if expected_type and not isinstance(record[col], expected_type):
                print(f"Column '{col}' expects {dtype}, got {type(record[col]).__name__}.")
                return False
        return True

    def insert(self, record):
        if not self.validate_record(record):
            return
        key = record.get(self.search_key)
        if key is None:
            print(f"Search key '{self.search_key}' not found in record.")
            return
        self.data.insert(key, record)

    def get(self, record_id):
        found, value = self.data.search(record_id)
        if found:
            return value
        return None

    def get_all(self):
        return self.data.get_all()

    def update(self, record_id, new_record):
        if not self.validate_record(new_record):
            return False
        return self.data.update(record_id, new_record)

    def delete(self, record_id):
        return self.data.delete(record_id)

    def range_query(self, start_value, end_value):
        return self.data.range_query(start_value, end_value)

    def visualize(self):
        return self.data.visualize_tree(filename=self.name)
