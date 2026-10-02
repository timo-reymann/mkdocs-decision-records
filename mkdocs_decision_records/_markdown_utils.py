import re
from collections.abc import Generator

_FENCE = re.compile(r"^ {0,3}(```|~~~)")
_ATX_H1 = re.compile(r"^ {0,3}#[ \t]+(.*)$")


def _strip_closing_hashes(text: str) -> str:
    """Drop an optional ATX closing sequence ("# Title ##"); it must follow whitespace."""
    stripped = text.rstrip("#")
    if stripped != text and (not stripped or stripped[-1] in " \t"):
        return stripped.rstrip()
    return text


def extract_first_h1(markdown: str | None) -> str | None:
    """Return the text of the first ATX level-1 heading, ignoring fenced code blocks."""
    if not markdown:
        return None
    in_fence = False
    for line in markdown.splitlines():
        if _FENCE.match(line):
            in_fence = not in_fence
        elif not in_fence and (match := _ATX_H1.match(line)):
            if title := _strip_closing_hashes(match.group(1).strip()):
                return title
    return None


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
