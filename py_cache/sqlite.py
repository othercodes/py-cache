import os
import time
from sqlite3 import Connection, IntegrityError
from typing import Any, Optional

import jsonpickle

from py_cache.contracts import Cache


class SQLiteCache(Cache):
    _create_sql = (
        'CREATE TABLE IF NOT EXISTS `entries` '
        '( `key` VARCHAR PRIMARY KEY, `value` VARCHAR, `expire_at` INTEGER)'
    )
    _create_index = 'CREATE INDEX IF NOT EXISTS `keyname_index` ON `entries` (`key`)'
    _get_sql = 'SELECT `value`, `expire_at` FROM `entries` WHERE `key` = ?'
    _del_sql = 'DELETE FROM `entries` WHERE `key` = ?'
    _del_expired_sql = 'DELETE FROM `entries` WHERE ? >= `expire_at`'
    _replace_sql = 'REPLACE INTO `entries` (`key`, `value`, `expire_at`) VALUES (?, ?, ?)'
    _insert_sql = 'INSERT INTO `entries` (`key`, `value`, `expire_at`) VALUES (?, ?, ?)'
    _clear_sql = 'DELETE FROM `entries`'

    _connection: Optional[Connection] = None

    def __init__(self, directory_path: str, ttl: int = 900, name: str = 'cache'):
        self.directory_path = directory_path.strip().rstrip('/')
        self.ttl = ttl
        self.name = name

        os.makedirs(self.directory_path, exist_ok=True)

    @property
    def connection(self) -> Connection:
        if self._connection:
            return self._connection

        connection = Connection(
            os.path.join(self.directory_path, f'{self.name}.sqlite'),
            timeout=15
        )

        with connection:
            connection.execute(self._create_sql)
            connection.execute(self._create_index)

        self._connection = connection

        return self._connection

    def has(self, key: str) -> bool:
        return self.get(key) is not None

    def get(self, key: str, default: Any = None) -> Any:
        try:
            with self.connection as connection:
                entry = next(connection.execute(self._get_sql, (key,)))

            if time.time() > entry[1]:
                with self.connection as connection:
                    connection.execute(self._del_sql, (key,))
                raise StopIteration

            return jsonpickle.decode(entry[0])
        except StopIteration:
            ttl = self.ttl
            value = default() if callable(default) else default

            if isinstance(value, tuple):
                value, ttl = value

        return value if value is None else self.put(key, value, ttl)

    def put(self, key: str, value: Any, ttl: Optional[int] = None) -> Any:
        serialized = jsonpickle.encode(value)
        expire_at = (self.ttl if ttl is None else ttl) + time.time()
        with self.connection as connection:
            try:
                connection.execute(self._insert_sql, (key, serialized, expire_at))
            except IntegrityError:
                connection.execute(self._replace_sql, (key, serialized, expire_at))

        return value

    def delete(self, key: str) -> None:
        with self.connection as connection:
            connection.execute(self._del_sql, (key,))

    def flush(self, expired_only: bool = False) -> None:
        with self.connection as connection:
            if expired_only:
                connection.execute(self._del_expired_sql, (time.time(),))
            else:
                connection.execute(self._clear_sql, )

    def __del__(self):
        if self.connection:
            self.connection.close()
