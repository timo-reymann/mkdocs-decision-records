from mkdocs_decision_records._markdown_utils import _list, _meta_table, extract_first_h1


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


def test_extract_first_h1():
    assert extract_first_h1("intro\n\n# Use Postgres\n\n## Context") == "Use Postgres"


def test_extract_first_h1_strips_closing_hashes():
    assert extract_first_h1("# Use Postgres ##") == "Use Postgres"


def test_extract_first_h1_ignores_h2_and_fenced_code():
    assert extract_first_h1("## Context\n```\n# comment\n```\n") is None


def test_extract_first_h1_none_or_empty():
    assert extract_first_h1(None) is None
    assert extract_first_h1("") is None


def test_extract_first_h1_keeps_hashes_that_are_part_of_the_title():
    assert extract_first_h1("# Adopt C#") == "Adopt C#"


def test_extract_first_h1_skips_empty_heading():
    assert extract_first_h1("# ##\n# Real title") == "Real title"
