from bplustree import BPlusTree


class Table:
    def __init__(self, name, schema, order=4, search_key=None):
        self.name = name
        self.schema = schema
        self.search_key = search_key
        self.tree = BPlusTree(order)

    def _validate(self, record):
        type_map = {"str": str, "int": int, "float": float, "bool": bool}
        for col, dtype in self.schema.items():
            if col not in record:
                raise ValueError(f"[{self.name}] Missing column '{col}'")
            expected = type_map.get(dtype)
            if expected and not isinstance(record[col], expected):
                raise TypeError(
                    f"[{self.name}] '{col}' must be {dtype}, got {type(record[col]).__name__}"
                )

    def insert(self, record):
        self._validate(record)
        key = record.get(self.search_key)
        if key is None:
            raise ValueError(f"Search key '{self.search_key}' missing in record.")
        self._raw_insert(key, record)

    def update(self, key, new_record):
        self._validate(new_record)
        found, _ = self.tree.search(key)
        if not found:
            raise ValueError(f"Key {key} not found in '{self.name}'.")
        self._raw_update(key, new_record)

    def delete(self, key):
        found, _ = self.tree.search(key)
        if not found:
            raise ValueError(f"Key {key} not found in '{self.name}'.")
        self._raw_delete(key)

    def _raw_insert(self, key, record):
        self.tree.insert(key, record)

    def _raw_update(self, key, record):
        self.tree.update(key, record)

    def _raw_delete(self, key):
        self.tree.delete(key)

    def _raw_search(self, key):
        return self.tree.search(key)

    def get(self, key):
        found, value = self.tree.search(key)
        return value if found else None

    def get_all(self):
        return self.tree.get_all()

    def range_query(self, start, end):
        return self.tree.range_query(start, end)
