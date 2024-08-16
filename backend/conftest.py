# conftest.py
import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

@pytest.fixture(autouse=True)
def add_imports(doctest_namespace):
    import asyncio
    doctest_namespace["asyncio"] = asyncio