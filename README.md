# Py-Cache

[![Test](https://github.com/othercodes/py-cache/actions/workflows/test.yml/badge.svg)](https://github.com/othercodes/py-cache/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/othercodes/py-cache/branch/master/graph/badge.svg?token=MSNTHXcCVC)](https://codecov.io/gh/othercodes/py-cache)

Small cache implementation for python.

## Installation

```bash
poetry add git+https://github.com/othercodes/py-cache.git
```

## Usage

Just initialize the class you want and use the public methods:

```python
from py_cache.contracts import Cache
from py_cache.sqlite import SQLiteCache


def some_process_that_requires_cache(cache: Cache):
    # retrieve the data from cache, ir the key is not cached yet and the default 
    # value is a callable the cache will use it to compute and cache the value
    user = cache.get('user-id', lambda: db_get_user('user-id'))

    print(user)


# inject the desired cache adapter.
cache = SQLiteCache('/tmp', 900)
some_process_that_requires_cache(cache)
```

Checking the if the key exists in the cache.

```python
cache.has('user-id')
```

Getting a value from the cache.

```python
# will return None if the value not exists in the cache.
cache.get('user-id')

# if the key is not present, the default value will be used.
cache.get('user-id', {'id': 'user-id', 'email': 'vincent.vega@mail.com'})

# if the default value is a callable the cache will use the callable to 
# compute and cache the request value.
cache.get('user-id', lambda: db_get_user('user-id'))

# you can also provide custom ttl (time to live) for a computed value by 
# returning a tuple of computed value and the ttl integer (Tuple[Any, int]).
cache.get('user-id', lambda: (db_get_user('user-id'), 3600))
```

Storing value by key in cache.

```python
# store the given value by key.
cache.put('user-id', {'id': 'user-id', 'email': 'vincent.vega@mail.com'})

# store the given value with custom ttl (time to live).
cache.put('user-id', {'id': 'user-id', 'email': 'vincent.vega@mail.com'}, 3600)
```

Delete a value from cache by key.

```python
cache.delete('user-id')
```

Flush the complete cache.

```python
cache.flush()
```

## Adapters

| Adapter          | Description                                |
|------------------|--------------------------------------------|
| FileSystemCache  | Uses simple json files to store the cache. |
| SQLiteCache      | SQLite will be used as cache.              |
