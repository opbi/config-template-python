"""python explicit namespace package for src.

This initializes the src package as a namespace package and root for resolving subdirectories to:
- Resolve files of the same name, e.g.
    - `api/order.py` and `lib/order.py`
    - `src/types.py` and system package `types`
"""
