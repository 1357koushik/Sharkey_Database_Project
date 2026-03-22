from graphviz import Digraph

class bplustreenode:
    def __init__(self, is_leaf=False):
        self.is_leaf = is_leaf
        self.keys = []
        self.children = []   # internal nodes
        self.values = []     # leaf nodes
        self.next = None     # leaf linkage
    def is_full(self, degree):  
        return len(self.keys) >= degree - 1


class bplustree:
    def __init__(self, degree=4):
        self.root = bplustreenode(True)
        self.degree = degree
        self.min_keys = (degree + 1) // 2 - 1   # for degree=4 -> 1

    
    # Search 
    
    def search(self, key):
        node = self.root
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]

        for i, item in enumerate(node.keys):
            if item == key:
                return (True, node.values[i])
        return (False, None)
    #Update
    def update(self, key, new_value):
        node = self.root
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]

        for i, item in enumerate(node.keys):
            if item == key:
                node.values[i] = new_value
                return True
        return False

    # Insert
    def insert(self, key, value):
        found,_ = self.search(key)
        if found:
          b=self.update(key,value)
          return
        if len(self.root.keys) == self.degree - 1:
            new_root = bplustreenode(is_leaf=False)
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
        new_node = bplustreenode(is_leaf=node.is_leaf)

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

    
    # Range query 
    def range_query(self, st, end):
        node = self.root
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and st >= node.keys[i]:
                i += 1
            node = node.children[i]

        result = []
        while node is not None:
            for i, key in enumerate(node.keys):
                if st <= key <= end:
                    result.append((key, node.values[i]))
                elif key > end:
                    return result
            node = node.next
        return result

    def get_all(self):
        result = []
        node = self.root
        while not node.is_leaf:
            node = node.children[0]

        while node:
            for key, value in zip(node.keys, node.values):
                result.append((key, value))
            node = node.next
        return result

    
    # Delete
    
    def delete(self, key):
        if not self.root or len(self.root.keys) == 0 and self.root.is_leaf:
            return False

        deleted = self._delete(self.root, key)

        if deleted:
            # Fix empty internal root
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
        # borrow from left sibling
        if idx > 0 and len(node.children[idx - 1].keys) > self.min_keys:
            self._borrow_from_prev(node, idx)
            return idx

        # borrow from right sibling
        if idx < len(node.children) - 1 and len(node.children[idx + 1].keys) > self.min_keys:
            self._borrow_from_next(node, idx)
            return idx

        # merge
        if idx < len(node.children) - 1:
            self._merge(node, idx)
            return idx
        else:
            self._merge(node, idx - 1)
            return idx - 1

    def _borrow_from_prev(self, node, index):
        child = node.children[index]
        sibling = node.children[index - 1]

        if child.is_leaf:
            child.keys.insert(0, sibling.keys.pop(-1))
            child.values.insert(0, sibling.values.pop(-1))
        else:
            child.keys.insert(0, node.keys[index - 1])
            node.keys[index - 1] = sibling.keys.pop(-1)
            child.children.insert(0, sibling.children.pop(-1))

    def _borrow_from_next(self, node, index):
        child = node.children[index]
        sibling = node.children[index + 1]

        if child.is_leaf:
            child.keys.append(sibling.keys.pop(0))
            child.values.append(sibling.values.pop(0))
        else:
            child.keys.append(node.keys[index])
            node.keys[index] = sibling.keys.pop(0)
            child.children.append(sibling.children.pop(0))

    def _merge(self, node, index):
        child = node.children[index]
        sibling = node.children[index + 1]

        if child.is_leaf:
            child.keys.extend(sibling.keys)
            child.values.extend(sibling.values)
            child.next = sibling.next
        else:
            child.keys.append(node.keys[index])
            child.keys.extend(sibling.keys)
            child.children.extend(sibling.children)

        node.keys.pop(index)
        node.children.pop(index + 1)

    
    # Rebuild internal separators
    
    def _leftmost_key(self, node):
        while node and not node.is_leaf:
            node = node.children[0]
        if node and node.keys:
            return node.keys[0]
        return None

    def _refresh_internal_keys(self, node):
        if node is None or node.is_leaf:
            return

        for child in node.children:
            self._refresh_internal_keys(child)

        new_keys = []
        for child in node.children[1:]:
            k = self._leftmost_key(child)
            if k is not None:
                new_keys.append(k)

        node.keys = new_keys

  
    # Visualization
   
    def visualize_tree(self, filename="bplustree"):
        dot = Digraph(format='png')
        dot.attr(dpi='300')
        dot.attr(rankdir='TB')

        self._add_nodes(dot, self.root)
        self._add_edges(dot, self.root)

        # Add dashed leaf links
        leaf = self.root
        while leaf and not leaf.is_leaf:
            leaf = leaf.children[0] if leaf.children else None

        while leaf and leaf.next:
            dot.edge(
                str(id(leaf)),
                str(id(leaf.next)),
                style='dashed',
                color='red',
                constraint='false'
            )
            leaf = leaf.next

        dot.render(filename, cleanup=True)
        return dot

    def _add_nodes(self, dot, node):
        if node is None:
            return

        node_id = str(id(node))
        label = " | ".join(str(k) for k in node.keys) if node.keys else "∅"

        if node.is_leaf:
            dot.node(node_id, label=label, shape="box", style="filled", color="lightblue")
        else:
            dot.node(node_id, label=label, shape="box", style="filled", color="lightgray")

        if not node.is_leaf:
            for child in node.children:
                self._add_nodes(dot, child)

    def _add_edges(self, dot, node):
        if node is None or node.is_leaf:
            return

        parent_id = str(id(node))
        for child in node.children:
            dot.edge(parent_id, str(id(child)))
            self._add_edges(dot, child)
