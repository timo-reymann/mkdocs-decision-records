from collections.abc import Generator


def _meta_table(items: list[tuple[str, str]]) -> Generator[str, None, None]:
    yield "<table>"
    for (h, v) in items:
        yield f"<tr><td><strong>{h}</strong></td><td>{v}</td></tr>"
    yield "</table>"


def _list(items: list[str]) -> Generator[str]:
    yield "<ul>"
    for item in items:
        yield f"<li>{item}</li>"
    yield "</ul>"
