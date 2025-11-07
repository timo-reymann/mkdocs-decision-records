import io
from unittest.mock import MagicMock

import pytest
import yaml
from mkdocs.structure.files import File

from mkdocs_decision_records.plugin import (
    CONFIG_LIFECYCLE_COLORS_KEY,
    CONFIG_TICKET_URL_PREFIX,
    DecisionRecordsPlugin,
    InvalidMetaDataError,
)


def _create_content(markdown: str, meta: dict):
    buffer = io.StringIO()
    yaml.dump(meta, buffer)
    return f"""\
---
{buffer.getvalue()}
---
{markdown}
"""


def test_on_page_markdown():
    plugin = DecisionRecordsPlugin()
    page = MagicMock()
    page.file.src_path = "adr/decision.md"
    page.meta = {
        "id": 1,
        "date": "2021-12-13",
        "deciders": ["decider1", "decider2"],
        "status": "accepted",
    }
    page.title = "Decision 1"
    files = MagicMock()
    markdown = "This is a decision record."
    result = plugin.on_page_markdown(markdown, page, {}, files)
    assert "Decision 1" in result


def test_on_files():
    plugin = DecisionRecordsPlugin()
    files = MagicMock()
    files.documentation_pages.return_value = [
        File.generated(
            MagicMock(),
            src_uri="adr-001",
            content=_create_content("# ADR 001 Some decision", {"id": "001"}),
        ),
        File.generated(
            MagicMock(),
            src_uri="adr-002",
            content=_create_content("# ADR 002 Some decision", {"id": "002"}),
        ),
        File.generated(
            MagicMock(),
            src_uri="misc",
            content=_create_content("# Misc", {}),
        ),
    ]
    plugin.on_files(files, config=MagicMock())
    assert 2 == len(plugin._dr_page_mapping)
    assert 2 in plugin._dr_page_mapping
    assert 1 in plugin._dr_page_mapping


def test_lifecycles():
    plugin = DecisionRecordsPlugin()
    assert isinstance(plugin.lifecycles, dict)


def test_required_deciders_count():
    plugin = DecisionRecordsPlugin()
    assert isinstance(plugin.required_deciders_count, int)


def test_create_status_badge():
    plugin = DecisionRecordsPlugin()
    page = MagicMock()
    page.meta = {"status": "accepted"}
    result = plugin._create_status_badge(page)
    assert "accepted" in result


def test_invalid_metadata_error():
    plugin = DecisionRecordsPlugin()
    page = MagicMock()
    page.file.src_path = "adr/decision.md"
    page.meta = {"id": 1, "date": "2021-12-13", "deciders": []}
    page.title = "Decision 1"
    files = MagicMock()
    files.documentation_pages.return_value = []
    markdown = "This is a decision record."
    with pytest.raises(InvalidMetaDataError):
        plugin.on_page_markdown(markdown, page, {}, files)


def test_ticket_text():
    plugin = DecisionRecordsPlugin()
    assert plugin._ticket_text("JIRA-1234") == "JIRA-1234"

    plugin.config[CONFIG_TICKET_URL_PREFIX] = "https://jira.company.com"
    assert (
        plugin._ticket_text("JIRA-1234")
        == "<a href='https://jira.company.com/JIRA-1234'>JIRA-1234</a>"
    )


@pytest.mark.parametrize(
    ["status_mapping", "status", "expected_result"],
    [
        [
            {},
            "accepted",
            (
                "<span style='color: "
                "white;background:#28a745;padding:.4em;border-radius:8px;font-size:100%;'>accepted</span>"
            ),
        ],
        [
            {"accepted": "#fff"},
            "accepted",
            (
                "<span style='color: "
                "white;background:#fff;padding:.4em;border-radius:8px;font-size:100%;'>accepted</span>"
            ),
        ],
        [
            {},
            "foo",
            None,
        ],
    ],
)
def test_create_status_badge(status_mapping, status, expected_result):
    plugin = DecisionRecordsPlugin()
    plugin.config[CONFIG_LIFECYCLE_COLORS_KEY] = status_mapping
    page = MagicMock()
    page.meta = {"status": status}
    if expected_result is not None:
        assert plugin._create_status_badge(page) == expected_result
    else:
        with pytest.raises(InvalidMetaDataError):
            plugin._create_status_badge(page)
