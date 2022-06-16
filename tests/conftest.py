from typing import List

import pytest

from py_cache.contracts import Cache
from py_cache.fs import FileSystemCache
from py_cache.null import NullCache
from py_cache.sqlite import SQLiteCache


@pytest.fixture
def adapters():
    def __adapters() -> List[Cache]:
        return [
            SQLiteCache('/tmp'),
            FileSystemCache('/tmp'),
            NullCache(),
        ]

    return __adapters
