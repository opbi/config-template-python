"""python explicit namespace package for tests.

see: https://packaging.python.org/guides/packaging-namespace-packages/

There are two test files with the same name, i.e. tests/shared/test_args.py and tests/test_args.py.
So, we need a __init__.py file in one of the folder to create an explicit namespace package to avoid conflict.
Otherwise, pytest will treat both test_order.py as the same module and only one will be executed.
"""
