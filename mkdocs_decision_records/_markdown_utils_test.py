from mkdocs_decision_records._markdown_utils import _list, _meta_table


def test_meta_table():
    assert list(_meta_table([("a", "b")])) == [
        '<table>',
        '<tr><td><strong>a</strong></td><td>b</td></tr>',
        '</table>',
    ]


def test_list():
    assert list(_list(["a"])) == ['<ul>', '<li>a</li>', '</ul>']


def test_meta_table_multiple_items():
    result = list(_meta_table([("Status", "accepted"), ("Date", "2024-01-01")]))
    assert result == [
        '<table>',
        '<tr><td><strong>Status</strong></td><td>accepted</td></tr>',
        '<tr><td><strong>Date</strong></td><td>2024-01-01</td></tr>',
        '</table>',
    ]


def test_meta_table_empty():
    result = list(_meta_table([]))
    assert result == ['<table>', '</table>']


def test_list_multiple_items():
    result = list(_list(["Alice", "Bob", "Charlie"]))
    assert result == [
        '<ul>',
        '<li>Alice</li>',
        '<li>Bob</li>',
        '<li>Charlie</li>',
        '</ul>',
    ]


def test_list_empty():
    result = list(_list([]))
    assert result == ['<ul>', '</ul>']
