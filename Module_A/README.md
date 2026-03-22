# Module A - Lightweight DBMS with B+ Tree Index
## CS432 Databases - IIT Gandhinagar - Semester II (2025-2026)
## Instructor: Dr. Yogesh K. Meena

---

## Quick Start

```bash
cd Module_A
pip install -r requirements.txt
jupyter notebook database/report.ipynb
```

Run all cells from top to bottom. The notebook covers all operations, benchmarking comparisons, and Graphviz visualizations.

---

## Project Structure

```
Module_A/
├── database/
│   ├── __init__.py       # Exports bplustree, Bruteforceindex, Table, DatabaseManager
│   ├── bplustree.py      # B+ Tree implementation
│   ├── bruteforce.py     # BruteForce index for performance comparison
│   ├── table.py          # Table abstraction built on top of B+ Tree
│   ├── db_manager.py     # DatabaseManager to manage multiple databases and tables
│   └── report.ipynb      # Full report with benchmarks, graphs, and visualizations
└── requirements.txt
```

---

## What I Built

This module is a lightweight in-memory database management system built from scratch. Instead of using SQLite or any existing database engine, I implemented my own indexing structure using a B+ Tree. The system supports multiple databases, each with multiple tables, and each table uses the B+ Tree as the internal storage and lookup engine.

---

## B+ Tree Implementation

The B+ Tree is in bplustree.py. There are two classes - bplustreenode which represents a single node, and bplustree which is the tree itself. The degree of the tree is configurable and defaults to 4.

### Node Structure

Each node has a list of keys, a list of children for internal nodes, a list of values for leaf nodes, and a next pointer for leaf nodes. The next pointer is what connects all leaf nodes in a linked list from left to right, which is what makes range queries efficient.

### Operations

**Search**

Starts at the root and walks down the tree. At each internal node it finds the correct child to follow by comparing the key against the separator keys. When it reaches a leaf node it scans the keys there and returns the value if found.

**Insert**

Before inserting it checks if the key already exists. If it does it calls update instead. If the root is full it creates a new root and splits the old root as the first step. Then it calls the recursive helper to find the correct leaf and insert there. If any node along the path is full it gets split before descending into it. After insertion it refreshes the internal separator keys from bottom up.

**Split**

For leaf nodes the split takes the right half of the keys and values into a new node, copies the first key of the new node up to the parent as a separator, and links the new node into the leaf linked list. For internal nodes the middle key is promoted up to the parent and removed from the child, and the right half of children goes into the new node.

**Delete**

Finds the key in the appropriate leaf and removes it. If the node drops below the minimum key count after deletion it tries to borrow from the left sibling first, then the right sibling. If neither sibling has a spare key it merges with one of them. After deletion the internal separator keys are refreshed.

**Range Query**

Traverses down to the leaf where the start key would be, then follows the next pointers across leaf nodes collecting all keys that fall within the range. Stops as soon as a key exceeds the end of the range.

**Update**

Traverses to the correct leaf and updates the value in place if the key exists. Returns True if successful, False if the key was not found.

**Get All**

Goes to the leftmost leaf node by always following the first child from the root down, then follows the next pointers across all leaf nodes collecting every key-value pair in sorted order.

---

## Table

The Table class in table.py wraps the B+ Tree and adds schema validation on top of it.

When you create a table you provide a name, a schema as a dictionary mapping column names to their expected types, the tree degree, and the column name to use as the search key.

When a record is inserted, the table checks that all columns defined in the schema are present in the record and that the values have the correct Python types. If validation fails the insert is rejected with an error message.

The Table class exposes insert, get, get all, update, delete, range query, and visualize. All of these delegate to the underlying B+ Tree.

---

## DatabaseManager

The DatabaseManager class in db_manager.py manages multiple named databases in memory. Each database is a dictionary of named Table objects.

It supports:

- create database and delete database
- list databases
- create table and delete table inside a database
- list tables in a database
- get table by name so you can run operations on it

---

## BruteForce Index

The Bruteforceindex class in bruteforce.py stores records in a plain Python list. Every operation iterates through the list from start to end. It is not meant to be efficient. It exists purely as a baseline to compare against the B+ Tree in the benchmarking section.

It supports insert, search, delete, update, get all, and range query. All of them run in O(n) time.

---

## Graphviz Visualization

The visualize_tree method generates a PNG image of the tree using graphviz.Digraph.

Internal nodes are shown as light gray boxes with their separator keys. Leaf nodes are shown as light blue boxes with their actual stored keys. Parent to child edges are solid black lines. Leaf to leaf connections are shown as dashed red arrows going from left to right, which shows the linked list structure.

The image is saved as a PNG file with 300 DPI resolution.

---

## Performance Analysis

The report notebook benchmarks the B+ Tree against BruteForce across the following:

- Insertion time at multiple dataset sizes
- Exact search time
- Deletion time
- Range query time across different range sizes
- Random mixed operations including inserts, searches and deletes
- Memory usage tracked using tracemalloc

All results are shown as Matplotlib line graphs with the B+ Tree and BruteForce plotted together on the same axes so the difference is clearly visible.

The B+ Tree is faster on search and range queries because it can find the starting point in O(log n) time and then scan forward using the leaf linked list. BruteForce has to scan the entire list every time. The insertion overhead for the B+ Tree is slightly higher because of node splitting but the search and query gains more than make up for it at scale.

---

## Requirements

```
graphviz
matplotlib
numpy
pandas
jupyter
```

Install with:

```bash
pip install -r requirements.txt
```

Note: The graphviz Python package also requires the Graphviz binary to be installed on your system.

On Windows, download from https://graphviz.org/download/ and add it to your PATH.

On Mac: brew install graphviz

On Ubuntu: sudo apt install graphviz

---

*CS432 Databases - Track 1 Assignment 2 - Module A*
