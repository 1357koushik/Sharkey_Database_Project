"""
bplustree.py — B+ Tree storage engine
"""


class BPlusTreeNode:
    def __init__(self, is_leaf=False):
        self.is_leaf = is_leaf
        self.keys = []
        self.children = []
        self.values = []
        self.next = None


class BPlusTree:
    def __init__(self, degree=4):
        self.root = BPlusTreeNode(is_leaf=True)
        self.degree = degree
        self.min_keys = (degree + 1) // 2 - 1

    def search(self, key):
        node = self.root
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
        for i, k in enumerate(node.keys):
            if k == key:
                return True, node.values[i]
        return False, None

    def insert(self, key, value):
        found, _ = self.search(key)
        if found:
            self.update(key, value)
            return
        if len(self.root.keys) == self.degree - 1:
            new_root = BPlusTreeNode(is_leaf=False)
            new_root.children.append(self.root)
            self._split_child(new_root, 0)
            self.root = new_root
        self._insert_non_full(self.root, key, value)
        self._refresh_internal_keys(self.root)

    def _insert_non_full(self, node, key, value):
        if node.is_leaf:
            idx = 0
            while idx < len(node.keys) and key > node.keys[idx]:
                idx += 1
            node.keys.insert(idx, key)
            node.values.insert(idx, value)
        else:
            idx = 0
            while idx < len(node.keys) and key > node.keys[idx]:
                idx += 1
            if len(node.children[idx].keys) == self.degree - 1:
                self._split_child(node, idx)
                if idx < len(node.keys) and key >= node.keys[idx]:
                    idx += 1
            self._insert_non_full(node.children[idx], key, value)

    def _split_child(self, parent, index):
        node = parent.children[index]
        new_node = BPlusTreeNode(is_leaf=node.is_leaf)
        if node.is_leaf:
            mid = len(node.keys) // 2
            new_node.keys = node.keys[mid:]
            new_node.values = node.values[mid:]
            node.keys = node.keys[:mid]
            node.values = node.values[:mid]
            parent.keys.insert(index, new_node.keys[0])
            parent.children.insert(index + 1, new_node)
            new_node.next = node.next
            node.next = new_node
        else:
            mid = len(node.keys) // 2
            up_key = node.keys[mid]
            new_node.keys = node.keys[mid + 1:]
            new_node.children = node.children[mid + 1:]
            node.keys = node.keys[:mid]
            node.children = node.children[:mid + 1]
            parent.keys.insert(index, up_key)
            parent.children.insert(index + 1, new_node)

    def update(self, key, new_value):
        node = self.root
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
        for i, k in enumerate(node.keys):
            if k == key:
                node.values[i] = new_value
                return True
        return False

    def delete(self, key):
        if not self.root or (len(self.root.keys) == 0 and self.root.is_leaf):
            return False
        deleted = self._delete(self.root, key)
        if deleted:
            while not self.root.is_leaf and len(self.root.keys) == 0 and self.root.children:
                self.root = self.root.children[0]
            self._refresh_internal_keys(self.root)
        return deleted

    def _delete(self, node, key):
        if node.is_leaf:
            if key in node.keys:
                idx = node.keys.index(key)
                node.keys.pop(idx)
                node.values.pop(idx)
                return True
            return False
        idx = 0
        while idx < len(node.keys) and key >= node.keys[idx]:
            idx += 1
        if len(node.children[idx].keys) == self.min_keys:
            idx = self._fill_child(node, idx)
        return self._delete(node.children[idx], key)

    def _fill_child(self, node, idx):
        if idx > 0 and len(node.children[idx - 1].keys) > self.min_keys:
            self._borrow_from_prev(node, idx)
            return idx
        if idx < len(node.children) - 1 and len(node.children[idx + 1].keys) > self.min_keys:
            self._borrow_from_next(node, idx)
            return idx
        if idx < len(node.children) - 1:
            self._merge(node, idx)
            return idx
        self._merge(node, idx - 1)
        return idx - 1

    def _borrow_from_prev(self, node, idx):
        child = node.children[idx]
        sibling = node.children[idx - 1]
        if child.is_leaf:
            child.keys.insert(0, sibling.keys.pop(-1))
            child.values.insert(0, sibling.values.pop(-1))
        else:
            child.keys.insert(0, node.keys[idx - 1])
            node.keys[idx - 1] = sibling.keys.pop(-1)
            child.children.insert(0, sibling.children.pop(-1))

    def _borrow_from_next(self, node, idx):
        child = node.children[idx]
        sibling = node.children[idx + 1]
        if child.is_leaf:
            child.keys.append(sibling.keys.pop(0))
            child.values.append(sibling.values.pop(0))
        else:
            child.keys.append(node.keys[idx])
            node.keys[idx] = sibling.keys.pop(0)
            child.children.append(sibling.children.pop(0))

    def _merge(self, node, idx):
        child = node.children[idx]
        sibling = node.children[idx + 1]
        if child.is_leaf:
            child.keys.extend(sibling.keys)
            child.values.extend(sibling.values)
            child.next = sibling.next
        else:
            child.keys.append(node.keys[idx])
            child.keys.extend(sibling.keys)
            child.children.extend(sibling.children)
        node.keys.pop(idx)
        node.children.pop(idx + 1)

    def _leftmost_key(self, node):
        while node and not node.is_leaf:
            node = node.children[0]
        return node.keys[0] if node and node.keys else None

    def _refresh_internal_keys(self, node):
        if node is None or node.is_leaf:
            return
        for child in node.children:
            self._refresh_internal_keys(child)
        node.keys = [self._leftmost_key(child) for child in node.children[1:] if self._leftmost_key(child) is not None]

    def get_all(self):
        result = []
        node = self.root
        while not node.is_leaf:
            node = node.children[0]
        while node:
            result.extend(zip(node.keys, node.values))
            node = node.next
        return result

    def range_query(self, start, end):
        node = self.root
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and start >= node.keys[i]:
                i += 1
            node = node.children[i]
        result = []
        while node:
            for i, key in enumerate(node.keys):
                if start <= key <= end:
                    result.append((key, node.values[i]))
                elif key > end:
                    return result
            node = node.next
        return result
