from mkdocs_decision_records._markdown_utils import _list, _meta_table


def test_meta_table():
    assert list(_meta_table([("a", "b")])) == [
        '<table>',
        '<tr><td><strong>a</strong></td><td>b</td></tr>',
        '</table>',
    ]

def test_list():
    assert list(_list(["a"])) == ['<ul>', '<li>a</li>', '</ul>']
