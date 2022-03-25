import os
import glob
from time import time
from typing import Any, Optional

import jsonpickle

from py_cache.contracts import Cache


class FileSystemCache(Cache):
    def __init__(self, directory_path: str, ttl: int = 900):
        self.directory_path = directory_path.strip().rstrip('/')
        self.ttl = ttl

    def _get_file_name(self, key: str) -> str:
        return f'{self.directory_path}/cache.{key}.json'

    def has(self, key: str) -> bool:
        return self.get(key) is not None

    def get(self, key: str, default: Any = None) -> Any:
        cache_file = self._get_file_name(key)
        try:
            with open(cache_file, 'r') as cache:
                content = jsonpickle.decode(cache.read())

            if int(time() - os.path.getmtime(cache_file)) >= content['ttl']:
                os.remove(self._get_file_name(key))
                raise FileNotFoundError

            return content['value']
        except FileNotFoundError:
            ttl = self.ttl
            value = default() if callable(default) else default

            if isinstance(value, tuple):
                value, ttl = value

        return value if value is None else self.put(key, value, ttl)

    def put(self, key: str, value: Any, ttl: Optional[int] = None) -> Any:
        with open(self._get_file_name(key), 'w') as cache:
            cache.write(jsonpickle.encode({
                'ttl': ttl if ttl else self.ttl,
                'value': value,
            }))

        return value

    def delete(self, key: str) -> None:
        try:
            print(self._get_file_name(key))
            os.remove(self._get_file_name(key))
        except FileNotFoundError:
            pass

    def flush(self) -> None:
        for file in glob.glob(self._get_file_name('*')):
            os.remove(file)
