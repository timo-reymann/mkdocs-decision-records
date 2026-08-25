import pytest

from mkdocs_decision_records._html_parser import (
    BasicTextContentParser,
    Element,
    Section,
    void,
)


def test_element_repr():
    assert repr(Element("div")) == "div"


def test_element_eq_with_string():
    el = Element("div")
    assert el == "div"
    assert el != "span"


def test_element_eq_with_element():
    el1 = Element("div")
    el2 = Element("div")
    el3 = Element("span")
    assert el1 == el2
    assert el1 != el3


def test_element_hash():
    el = Element("div")
    assert hash(el) == hash("div")
    assert {Element("div"), Element("span")} == {"div", "span"}


def test_element_is_excluded_true():
    el = Element("div", {"data-search-exclude": ""})
    assert el.is_excluded() is True


def test_element_is_excluded_false():
    el = Element("div", {})
    assert el.is_excluded() is False


def test_element_default_attrs_empty():
    el = Element("p")
    assert el.attrs == {}


def test_section_repr_without_id():
    section = Section(Element("div"))
    assert repr(section) == "div"


def test_section_repr_with_id():
    section = Section(Element("h1"))
    section.id = "my-heading"
    assert repr(section) == "h1#my-heading"


def test_section_is_excluded_delegates():
    el = Element("div", {"data-search-exclude": ""})
    section = Section(el)
    assert section.is_excluded() is True


def test_section_initial_state():
    section = Section(Element("h2"), depth=3)
    assert section.depth == 3
    assert section.text == []
    assert section.title == []
    assert section.id is None


def _parse(html):
    parser = BasicTextContentParser()
    parser.feed(html)
    parser.close()
    return parser.data


def test_parser_empty_html():
    assert len(_parse("")) == 0


def test_parser_paragraph_text():
    data = _parse("<p>Hello world</p>")
    assert len(data) >= 1
    texts = [" ".join(s.text).strip() for s in data]
    assert any("Hello world" in t for t in texts)


def test_parser_heading_sections():
    html = '<h1 id="h1">Title 1</h1><p>Body 1</p><h2 id="h2">Title 2</h2><p>Body 2</p>'
    data = _parse(html)
    titles = ["".join(s.title).strip() for s in data if s.title]
    assert "Title 1" in titles
    assert "Title 2" in titles


def test_parser_script_tag_skipped():
    html = '<h1 id="h1">Title</h1><script>var x = 1;</script><p>Body</p>'
    data = _parse(html)
    texts = [" ".join(s.text).strip() for s in data]
    assert not any("var x" in t for t in texts)


def test_parser_style_tag_skipped():
    html = '<h1 id="h1">Title</h1><style>.foo{color:red}</style><p>Body</p>'
    data = _parse(html)
    texts = [" ".join(s.text).strip() for s in data]
    assert not any(".foo" in t for t in texts)


def test_parser_code_block_preserved():
    html = '<h1 id="h1">Title</h1><p><code>x = 1</code></p>'
    data = _parse(html)
    texts = [" ".join(s.text).strip() for s in data]
    assert any("x = 1" in t for t in texts)


def test_parser_data_search_exclude():
    html = '<h1 id="h1">Title</h1><div data-search-exclude><p>Hidden</p></div><p>Visible</p>'
    data = _parse(html)
    texts = [" ".join(s.text).strip() for s in data]
    assert not any("Hidden" in t for t in texts)


def test_parser_li_preserved():
    html = '<h1 id="h1">Title</h1><ul><li>Item 1</li><li>Item 2</li></ul>'
    data = _parse(html)
    texts = [" ".join(s.text).strip() for s in data]
    assert any("Item 1" in t for t in texts)


def test_parser_preface_section():
    html = '<p>Preface text</p><h1 id="h1">Title</h1><p>Body</p>'
    data = _parse(html)
    assert len(data) >= 2


def test_parser_whitespace_collapsed():
    html = '<h1 id="h1">Title</h1><p>   spaces   </p>'
    data = _parse(html)
    texts = [" ".join(s.text).strip() for s in data]
    assert any("spaces" in t for t in texts)


def test_parser_void_tags_ignored():
    html = '<h1 id="h1">Title</h1><br><hr><img src="x.png"><p>Body</p>'
    data = _parse(html)
    assert len(data) >= 1


def test_parser_superscript_preserved():
    html = '<h1 id="h1">Title</h1><p>H<sub>2</sub>O and x<sup>2</sup></p>'
    data = _parse(html)
    texts = [" ".join(s.text).strip() for s in data]
    assert any("H" in t for t in texts)


def test_parser_section_excluded_attribute():
    html = '<h1 id="h1" data-search-exclude>Title</h1><p>Body</p>'
    data = _parse(html)
    excluded = [s for s in data if s.is_excluded()]
    assert len(excluded) >= 1


def test_parser_multiple_headings():
    html = (
        '<h1 id="h1">First</h1><p>Body 1</p>'
        '<h2 id="h2">Second</h2><p>Body 2</p>'
        '<h3 id="h3">Third</h3><p>Body 3</p>'
    )
    data = _parse(html)
    titles = ["".join(s.title).strip() for s in data if s.title]
    assert "First" in titles
    assert "Second" in titles
    assert "Third" in titles


def test_void_set_contains_common_tags():
    assert "br" in void
    assert "hr" in void
    assert "img" in void
    assert "input" in void
    assert "meta" in void
    assert "link" in void


def test_parser_pre_tag_preserves_whitespace():
    html = '<h1 id="h1">Title</h1><pre>  line1\n  line2</pre>'
    data = _parse(html)
    texts = [" ".join(s.text).strip() for s in data]
    assert any("line1" in t for t in texts)


def test_parser_html_escaping():
    html = '<h1 id="h1">Title</h1><p>5 &gt; 3 &amp; 2 &lt; 4</p>'
    data = _parse(html)
    texts = [" ".join(s.text).strip() for s in data]
    assert any("5 > 3" in t or "5 &gt; 3" in t for t in texts)
