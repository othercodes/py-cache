from py_cache.fs import FileSystemCache


def test_filesystem_cache_should_return_false_if_has_not_cached_key():
    fs = FileSystemCache('/tmp')

    assert not fs.has('missing-key')


def test_filesystem_cache_should_cache_values_by_key():
    fs = FileSystemCache('/tmp', 0)

    on_db = {'id': 1, 'email': 'vincent.vega@mail.com'}

    user_one = fs.get(str(on_db['id']), lambda: (on_db, 5))
    user_two = fs.get(str(on_db['id']))

    assert on_db == user_one == user_two
    assert fs.has(str(on_db['id']))


def test_filesystem_cache_should_delete_value_by_key():
    fs = FileSystemCache('/tmp', 500)

    fs.put('123', 'some-value')
    fs.delete('123')
    fs.delete('missing-key')

    assert not fs.has('123')
    assert not fs.has('missing-key')

def test_filesystem_cache_should_flush_all_values():
    fs = FileSystemCache('/tmp', 500)

    fs.put('123', 'some-value-1')
    fs.put('124', 'some-value-2')
    fs.put('125', 'some-value-3')

    fs.flush()

    assert not fs.has('123')
    assert not fs.has('124')
    assert not fs.has('125')
