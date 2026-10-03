import io
from unittest.mock import MagicMock

import pytest
import yaml
from mkdocs.structure.files import File, Files

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
    page.file.src_uri = "adr/decision.md"
    page.file.page = page
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


def test_on_page_markdown_does_not_flag_self_as_duplicate():
    # MkDocs' own frontmatter parser resolves ids like 008/009 as plain
    # strings (8/9 are not valid octal digits), unlike 000-007 which resolve
    # to int. A page must never be considered a duplicate of itself
    # regardless of how its raw id was typed.
    plugin = DecisionRecordsPlugin()
    page = MagicMock()
    page.file.src_uri = "adr/008-decision.md"
    page.file.src_path = "adr/008-decision.md"
    page.file.page = page
    page.meta = {
        "id": "008",
        "date": "2021-12-13",
        "deciders": ["decider1"],
        "status": "accepted",
    }
    page.title = "Decision 8"
    files = MagicMock()
    files.documentation_pages.return_value = [page.file]
    markdown = "This is a decision record."
    result = plugin.on_page_markdown(markdown, page, {}, files)
    assert "Decision 8" in result


def test_on_page_markdown_raises_on_duplicate_id_across_pages():
    plugin = DecisionRecordsPlugin()
    other_file = MagicMock()
    other_file.src_path = "adr/003-other-decision.md"
    other_file.page.meta = {
        "id": 3,
        "date": "2021-12-13",
        "deciders": ["decider1"],
        "status": "accepted",
    }
    page = MagicMock()
    page.file.src_uri = "adr/003-decision.md"
    page.file.src_path = "adr/003-decision.md"
    page.file.page = page
    page.meta = {
        "id": 3,
        "date": "2021-12-13",
        "deciders": ["decider1"],
        "status": "accepted",
    }
    page.title = "Decision 3"
    files = MagicMock()
    files.documentation_pages.return_value = [page.file, other_file]
    markdown = "This is a decision record."
    with pytest.raises(InvalidMetaDataError):
        plugin.on_page_markdown(markdown, page, {}, files)


def test_on_page_markdown_superseded_padded():
    plugin = DecisionRecordsPlugin()
    page_superseded = MagicMock()
    page_superseded.file.src_path = "adr/002-decision.md"
    page_superseded.file.src_uri = "adr/002-decision.md"
    page_superseded.page = page_superseded
    page_superseded.meta = {
        "id": 2,
        "date": "2021-12-13",
        "deciders": ["decider1"],
        "status": "accepted",
    }
    page_superseded.title = "Decision 2"
    plugin._dr_page_mapping["002"] = page_superseded
    page = MagicMock()
    page.file.src_uri = "adr/decision.md"
    page.file.page = page
    page.meta = {
        "id": 1,
        "date": "2021-12-13",
        "deciders": ["decider1", "decider2"],
        "status": "superseded",
        "superseded_by": "002",
    }
    page.title = "Decision 1"
    files = MagicMock()
    markdown = "This is a decision record."
    result = plugin.on_page_markdown(markdown, page, {}, files)
    assert "Decision 1" in result


def test_on_page_markdown_superseded_int():
    plugin = DecisionRecordsPlugin()
    page_superseded = MagicMock()
    page_superseded.file.src_path = "adr/002-decision.md"
    page_superseded.file.src_uri = "adr/002-decision.md"
    page_superseded.page = page_superseded
    page_superseded.meta = {
        "id": 2,
        "date": "2021-12-13",
        "deciders": ["decider1"],
        "status": "accepted",
    }
    page_superseded.title = "Decision 2"
    plugin._dr_page_mapping["002"] = page_superseded
    page = MagicMock()
    page.file.src_uri = "adr/decision.md"
    page.file.page = page
    page.meta = {
        "id": 1,
        "date": "2021-12-13",
        "deciders": ["decider1", "decider2"],
        "status": "superseded",
        "superseded_by": 2,
    }
    page.title = "Decision 1"
    files = MagicMock()
    markdown = "This is a decision record."
    result = plugin.on_page_markdown(markdown, page, {}, files)
    assert "Decision 1" in result


def test_on_page_markdown_superseded_invalid():
    plugin = DecisionRecordsPlugin()
    page = MagicMock()
    page.file.src_uri = "adr/decision.md"
    page.file.page = page
    page.meta = {
        "id": 1,
        "date": "2021-12-13",
        "deciders": ["decider1", "decider2"],
        "status": "superseded",
        "superseded_by": "3",
    }
    page.title = "Decision 1"
    files = MagicMock()
    markdown = "This is a decision record."
    with pytest.raises(InvalidMetaDataError):
        plugin.on_page_markdown(markdown, page, {}, files)


def test_on_files():
    plugin = DecisionRecordsPlugin()
    files = MagicMock()
    files.documentation_pages.return_value = [
        File.generated(
            MagicMock(),
            src_uri="adr-001",
            content=_create_content("# ADR 001 Some decision", {"id": "001", "status": "accepted", "date": "2024-01-01"}),
        ),
        File.generated(
            MagicMock(),
            src_uri="adr-002",
            content=_create_content("# ADR 002 Some decision", {"id": "002", "status": "accepted", "date": "2024-01-01"}),
        ),
        File.generated(
            MagicMock(),
            src_uri="misc",
            content=_create_content("# Misc", {}),
        ),
    ]
    plugin.on_files(files, config=MagicMock())
    assert 2 == len(plugin._dr_page_mapping)
    assert "002" in plugin._dr_page_mapping
    assert "001" in plugin._dr_page_mapping


def test_on_files_ignores_non_decision_folder_files_with_non_integer_ids():
    """Test that files outside the decisions folder with non-integer IDs are ignored"""
    plugin = DecisionRecordsPlugin()
    plugin._dr_page_mapping = {}  # Clear any shared state
    files = MagicMock()
    files.documentation_pages.return_value = [
        File.generated(
            MagicMock(),
            src_uri="adr/adr-001",
            content=_create_content("# ADR 001 Some decision", {"id": "001", "status": "accepted", "date": "2024-01-01"}),
        ),
        File.generated(
            MagicMock(),
            src_uri="docs/system-model",
            content=_create_content("# System Model", {"id": "system-model"}),
        ),
        File.generated(
            MagicMock(),
            src_uri="guides/architecture",
            content=_create_content("# Architecture", {"id": "not-a-number"}),
        ),
    ]
    # This should not raise a ValueError
    plugin.on_files(files, config=MagicMock())
    # Only the file in the adr folder should be processed
    assert 1 == len(plugin._dr_page_mapping)
    assert "001" in plugin._dr_page_mapping


def test_lifecycles():
    plugin = DecisionRecordsPlugin()
    assert isinstance(plugin.lifecycles, dict)


def test_required_deciders_count():
    plugin = DecisionRecordsPlugin()
    assert isinstance(plugin.required_deciders_count, int)


def test_create_status_badge():
    plugin = DecisionRecordsPlugin()
    dr = MagicMock()
    dr.status = "accepted"
    dr.file.page = MagicMock()
    result = plugin._create_status_badge(dr)
    assert "accepted" in result


def test_invalid_metadata_error():
    from mkdocs.exceptions import PluginError

    plugin = DecisionRecordsPlugin()
    page = MagicMock()
    page.file.src_uri = "adr/decision.md"
    page.file.page = page
    page.meta = {"id": 1, "date": "2021-12-13", "status": "", "deciders": []}
    page.title = "Decision 1"
    files = MagicMock()
    files.documentation_pages.return_value = []
    markdown = "This is a decision record."
    with pytest.raises(PluginError):
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
    dr = MagicMock()
    dr.status = status
    dr.file.page = MagicMock()
    if expected_result is not None:
        assert plugin._create_status_badge(dr) == expected_result
    else:
        with pytest.raises(InvalidMetaDataError):
            plugin._create_status_badge(dr)


def test_on_files_with_nested_decisions_folder():
    """Test that on_files works with nested decisions_folder like 'internal/adr'"""
    from mkdocs_decision_records.plugin import CONFIG_DECISIONS_FOLDER_KEY

    plugin = DecisionRecordsPlugin()
    plugin.config[CONFIG_DECISIONS_FOLDER_KEY] = "internal/adr"
    plugin._dr_page_mapping = {}
    files = MagicMock()
    files.documentation_pages.return_value = [
        File.generated(
            MagicMock(),
            src_uri="internal/adr/001-decision.md",
            content=_create_content("# ADR 001", {"id": "001", "status": "accepted", "date": "2024-01-01"}),
        ),
        File.generated(
            MagicMock(),
            src_uri="other/docs/file.md",
            content=_create_content("# Other", {"id": "other"}),
        ),
    ]
    plugin.on_files(files, config=MagicMock())
    assert 1 == len(plugin._dr_page_mapping)
    assert "001" in plugin._dr_page_mapping


def test_on_page_markdown_with_nested_decisions_folder():
    """Test that on_page_markdown works with nested decisions_folder"""
    from mkdocs_decision_records.plugin import CONFIG_DECISIONS_FOLDER_KEY

    plugin = DecisionRecordsPlugin()
    plugin.config[CONFIG_DECISIONS_FOLDER_KEY] = "internal/adr"
    page = MagicMock()
    page.file.src_uri = "internal/adr/decision.md"
    page.file.page = page
    page.meta = {
        "id": 1,
        "date": "2021-12-13",
        "deciders": ["decider1"],
        "status": "accepted",
    }
    page.title = "Decision 1"
    files = MagicMock()
    files.documentation_pages.return_value = []
    markdown = "This is a decision record."
    result = plugin.on_page_markdown(markdown, page, {}, files)
    assert "Decision 1" in result


def test_on_page_markdown_ignores_file_outside_nested_decisions_folder():
    """Test that files outside nested decisions_folder are ignored"""
    from mkdocs_decision_records.plugin import CONFIG_DECISIONS_FOLDER_KEY

    plugin = DecisionRecordsPlugin()
    plugin.config[CONFIG_DECISIONS_FOLDER_KEY] = "internal/adr"
    page = MagicMock()
    page.file.src_uri = "other/docs/file.md"
    page.meta = {"id": 1}
    page.title = "Other File"
    files = MagicMock()
    markdown = "This is not a decision record."
    result = plugin.on_page_markdown(markdown, page, {}, files)
    # Should return unchanged markdown since file is outside decisions_folder
    assert result == markdown


def test_decisions_folder_with_backslashes_is_normalized():
    """Test that decisions_folder with backslashes (Windows) is normalized"""
    from mkdocs_decision_records.plugin import CONFIG_DECISIONS_FOLDER_KEY

    plugin = DecisionRecordsPlugin()
    # Windows-style path with backslashes
    plugin.config[CONFIG_DECISIONS_FOLDER_KEY] = "internal\\adr"
    plugin._dr_page_mapping = {}
    files = MagicMock()
    files.documentation_pages.return_value = [
        File.generated(
            MagicMock(),
            src_uri="internal/adr/001-decision.md",
            content=_create_content("# ADR 001", {"id": "001", "status": "accepted", "date": "2024-01-01"}),
        ),
    ]
    plugin.on_files(files, config=MagicMock())
    # Should still match because backslashes are normalized to forward slashes
    assert 1 == len(plugin._dr_page_mapping)


def test_decisions_folder_with_trailing_slash_is_normalized():
    """Test that decisions_folder with trailing slash is normalized"""
    from mkdocs_decision_records.plugin import CONFIG_DECISIONS_FOLDER_KEY

    plugin = DecisionRecordsPlugin()
    plugin.config[CONFIG_DECISIONS_FOLDER_KEY] = "adr/"
    plugin._dr_page_mapping = {}
    files = MagicMock()
    files.documentation_pages.return_value = [
        File.generated(
            MagicMock(),
            src_uri="adr/001-decision.md",
            content=_create_content("# ADR 001", {"id": "001", "status": "accepted", "date": "2024-01-01"}),
        ),
    ]
    plugin.on_files(files, config=MagicMock())
    assert 1 == len(plugin._dr_page_mapping)


def test_id_length_default():
    """Test that id_length defaults to 3"""
    from mkdocs_decision_records.plugin import CONFIG_DECISION_ID_LENGTH_DEFAULT

    plugin = DecisionRecordsPlugin()
    assert plugin.id_length == CONFIG_DECISION_ID_LENGTH_DEFAULT
    assert plugin.id_length == 3


def test_id_length_custom():
    """Test that id_length can be configured to a custom value"""
    from mkdocs_decision_records.plugin import CONFIG_DECISION_ID_LENGTH_KEY

    plugin = DecisionRecordsPlugin()
    plugin.config[CONFIG_DECISION_ID_LENGTH_KEY] = 4
    assert plugin.id_length == 4


def test_validate_id_length_default():
    """Test that validate_id_length defaults to False"""
    from mkdocs_decision_records.plugin import (
        CONFIG_DECISION_ID_LENGTH_VALIDATE_DEFAULT,
    )

    plugin = DecisionRecordsPlugin()
    assert plugin.validate_id_length == CONFIG_DECISION_ID_LENGTH_VALIDATE_DEFAULT
    assert plugin.validate_id_length is False


def test_validate_id_length_custom():
    """Test that validate_id_length can be configured"""
    from mkdocs_decision_records.plugin import CONFIG_DECISION_ID_LENGTH_VALIDATE_KEY

    plugin = DecisionRecordsPlugin()
    plugin.config[CONFIG_DECISION_ID_LENGTH_VALIDATE_KEY] = True
    assert plugin.validate_id_length is True




def test_on_page_markdown_with_4_digit_id_length():
    """Test that on_page_markdown formats IDs with 4 digits when configured"""
    from mkdocs_decision_records.plugin import (
        CONFIG_DECISION_ID_LENGTH_KEY,
        CONFIG_DECISION_ID_LENGTH_VALIDATE_KEY,
    )

    plugin = DecisionRecordsPlugin()
    plugin.config[CONFIG_DECISION_ID_LENGTH_KEY] = 4
    plugin.config[CONFIG_DECISION_ID_LENGTH_VALIDATE_KEY] = False
    page = MagicMock()
    page.file.src_uri = "adr/decision.md"
    page.file.page = page
    page.meta = {
        "id": 1,
        "date": "2021-12-13",
        "deciders": ["decider1"],
        "status": "accepted",
    }
    page.title = "Decision 1"
    files = MagicMock()
    files.documentation_pages.return_value = []
    markdown = "This is a decision record."
    result = plugin.on_page_markdown(markdown, page, {}, files)
    assert "0001 - Decision 1" in result


def test_on_page_markdown_with_validation_enabled():
    """Test that validation triggers when validate_id_length is enabled"""
    from mkdocs_decision_records.plugin import (
        CONFIG_DECISION_ID_LENGTH_KEY,
        CONFIG_DECISION_ID_LENGTH_VALIDATE_KEY,
    )
    from mkdocs.exceptions import PluginError

    plugin = DecisionRecordsPlugin()
    plugin.config[CONFIG_DECISION_ID_LENGTH_KEY] = 4
    plugin.config[CONFIG_DECISION_ID_LENGTH_VALIDATE_KEY] = True
    page = MagicMock()
    page.file.src_uri = "adr/decision.md"
    page.file.page = page
    page.meta = {
        "id": 12345,
        "date": "2021-12-13",
        "deciders": ["decider1"],
        "status": "accepted",
    }
    page.title = "Decision 12345"
    files = MagicMock()
    markdown = "This is a decision record."
    with pytest.raises(PluginError):
        plugin.on_page_markdown(markdown, page, {}, files)


def test_on_page_markdown_with_validation_enabled_valid_id():
    """Test that valid length IDs pass validation when validate_id_length is enabled"""
    from mkdocs_decision_records.plugin import (
        CONFIG_DECISION_ID_LENGTH_KEY,
        CONFIG_DECISION_ID_LENGTH_VALIDATE_KEY,
    )

    plugin = DecisionRecordsPlugin()
    plugin.config[CONFIG_DECISION_ID_LENGTH_KEY] = 4
    plugin.config[CONFIG_DECISION_ID_LENGTH_VALIDATE_KEY] = True
    page = MagicMock()
    page.file.src_uri = "adr/decision.md"
    page.file.page = page
    page.meta = {
        "id": "0001",
        "date": "2021-12-13",
        "deciders": ["decider1"],
        "status": "accepted",
    }
    page.title = "0001 - My Decision"
    files = MagicMock()
    files.documentation_pages.return_value = []
    markdown = "This is a decision record."
    result = plugin.on_page_markdown(markdown, page, {}, files)
    assert "0001 - My Decision" in result


def test_on_page_markdown_with_validation_enabled_int_id_padded():
    """YAML parses `id: 0001` as int 1 — validation should accept it when it fits the configured length."""
    from mkdocs_decision_records.plugin import (
        CONFIG_DECISION_ID_LENGTH_KEY,
        CONFIG_DECISION_ID_LENGTH_VALIDATE_KEY,
    )

    plugin = DecisionRecordsPlugin()
    plugin.config[CONFIG_DECISION_ID_LENGTH_KEY] = 4
    plugin.config[CONFIG_DECISION_ID_LENGTH_VALIDATE_KEY] = True
    page = MagicMock()
    page.file.src_uri = "adr/decision.md"
    page.file.page = page
    page.meta = {
        "id": "0001",
        "date": "2021-12-13",
        "deciders": ["decider1"],
        "status": "accepted",
    }
    page.title = "0001 - My Decision"
    files = MagicMock()
    files.documentation_pages.return_value = []
    markdown = "This is a decision record."
    result = plugin.on_page_markdown(markdown, page, {}, files)
    assert "0001 - My Decision" in result


def test_on_page_markdown_template_with_custom_id_length():
    """Test that template title uses the configured ID length"""
    from mkdocs_decision_records.plugin import (
        CONFIG_DECISION_ID_LENGTH_KEY,
        CONFIG_DECISION_ID_LENGTH_VALIDATE_KEY,
    )

    plugin = DecisionRecordsPlugin()
    plugin.config[CONFIG_DECISION_ID_LENGTH_KEY] = 4
    plugin.config[CONFIG_DECISION_ID_LENGTH_VALIDATE_KEY] = False
    page = MagicMock()
    page.file.src_uri = "adr/0001-template.md"
    page.file.page = page
    page.meta = {
        "id": 0,
        "date": "2021-12-13",
        "deciders": ["decider1"],
        "status": "proposed",
    }
    page.title = "Template"
    files = MagicMock()
    markdown = "This is a template."
    result = plugin.on_page_markdown(markdown, page, {}, files)
    assert page.title == "0000 - Template"


def test_on_files_with_validation_enabled_invalid_id():
    """Test that on_files raises error with validation enabled for invalid length IDs"""
    from mkdocs_decision_records.plugin import (
        CONFIG_DECISION_ID_LENGTH_KEY,
        CONFIG_DECISION_ID_LENGTH_VALIDATE_KEY,
    )
    from mkdocs.exceptions import PluginError

    plugin = DecisionRecordsPlugin()
    plugin.config[CONFIG_DECISION_ID_LENGTH_KEY] = 4
    plugin.config[CONFIG_DECISION_ID_LENGTH_VALIDATE_KEY] = True
    files = MagicMock()
    files.documentation_pages.return_value = [
        File.generated(
            MagicMock(),
            src_uri="adr/001-decision.md",
            content=_create_content("# ADR 001", {"id": "001", "status": "accepted", "date": "2024-01-01"}),
        ),
    ]
    with pytest.raises(PluginError):
        plugin.on_files(files, config=MagicMock())


def test_on_files_with_validation_enabled_valid_id():
    """Test that on_files accepts valid length IDs with validation enabled"""
    from mkdocs_decision_records.plugin import (
        CONFIG_DECISION_ID_LENGTH_KEY,
        CONFIG_DECISION_ID_LENGTH_VALIDATE_KEY,
    )

    plugin = DecisionRecordsPlugin()
    plugin.config[CONFIG_DECISION_ID_LENGTH_KEY] = 4
    plugin.config[CONFIG_DECISION_ID_LENGTH_VALIDATE_KEY] = True
    plugin._dr_page_mapping = {}
    files = MagicMock()
    files.documentation_pages.return_value = [
        File.generated(
            MagicMock(),
            src_uri="adr/0001-decision.md",
            content=_create_content("# ADR 0001", {"id": "0001", "status": "accepted", "date": "2024-01-01"}),
        ),
    ]
    plugin.on_files(files, config=MagicMock())
    assert 1 == len(plugin._dr_page_mapping)


def _dr_mock(*, status="accepted", superseded_by=None, deciders=None, ticket=None, is_template=False):
    dr = MagicMock()
    dr.is_template.return_value = is_template
    dr.id = "001"
    dr.date.isoformat.return_value = "2024-01-01"
    dr.title = "001 - Some decision"
    dr.status = status
    dr.superseded_by = superseded_by
    dr.deciders = deciders
    dr.ticket = ticket
    dr.file.url = "adr/001-some-decision/"
    dr.file.page.content = "<h1 id='x'>001 - Some decision</h1><p>Body text</p>"
    dr.file.page.toc = "toc"
    return dr


def test_generate_index_includes_url_deciders_and_ticket():
    plugin = DecisionRecordsPlugin()
    plugin._dr_page_mapping = {
        "001": _dr_mock(deciders=["Alice", "Bob"], ticket="FOO-1"),
    }

    [entry] = list(plugin._generate_index())

    assert entry["url"] == "adr/001-some-decision/"
    assert entry["deciders"] == ["Alice", "Bob"]
    assert entry["ticket"] == "FOO-1"


def test_generate_index_defaults_deciders_and_ticket():
    """A record without deciders/ticket frontmatter still carries the keys."""
    plugin = DecisionRecordsPlugin()
    plugin._dr_page_mapping = {"001": _dr_mock(deciders=[], ticket=None)}

    [entry] = list(plugin._generate_index())

    assert entry["deciders"] == []
    assert entry["ticket"] is None


def test_generate_index_excludes_template():
    plugin = DecisionRecordsPlugin()
    plugin._dr_page_mapping = {"000": _dr_mock(is_template=True)}

    assert list(plugin._generate_index()) == []


def test_generate_index_superseded_by_only_present_when_superseded():
    plugin = DecisionRecordsPlugin()
    plugin._dr_page_mapping = {
        "001": _dr_mock(status="superseded", superseded_by="002"),
    }

    [entry] = list(plugin._generate_index())

    assert entry["superseded_by"] == "002"


def test_generate_index_no_superseded_by_when_not_superseded():
    plugin = DecisionRecordsPlugin()
    plugin._dr_page_mapping = {"001": _dr_mock(status="accepted")}

    [entry] = list(plugin._generate_index())

    assert "superseded_by" not in entry


def _index_dr_mock(
    *,
    dr_id="001",
    title=None,
    status="accepted",
    deciders=None,
    ticket=None,
    is_template=False,
    src_uri=None,
    date="2024-01-01",
):
    dr = MagicMock()
    dr.is_template.return_value = is_template
    dr.id = dr_id
    dr.date.isoformat.return_value = date
    dr.title = title if title is not None else f"{dr_id} - Some decision"
    dr.status = status
    dr.deciders = deciders if deciders is not None else []
    dr.ticket = ticket
    dr.file.src_uri = src_uri or f"adr/{dr_id}-some-decision.md"
    dr.file.url = dr.file.src_uri.replace(".md", "/")
    return dr


def _index_file(src_uri="adr/index.md") -> File:
    return File.generated(MagicMock(), src_uri=src_uri, content="")


def _index_plugin(**options) -> DecisionRecordsPlugin:
    # BasePlugin.config is a class-level dict shared by every instance, so
    # load_config() is used to give each test an isolated instance config.
    plugin = DecisionRecordsPlugin()
    errors, _warnings = plugin.load_config(options)
    assert not errors
    plugin._dr_page_mapping = {}
    return plugin


def _index_rows(markdown: str) -> list[list[str]]:
    rows = []
    for line in markdown.splitlines():
        if not line.startswith("|") or line.startswith("|---") or line.startswith("| ID "):
            continue
        rows.append([cell.strip() for cell in line.strip("|").split("|")])
    return rows


def test_generate_index_page_default_is_false():
    plugin = _index_plugin()

    assert plugin.generate_index_page is False


def test_build_index_markdown_header_columns():
    plugin = _index_plugin()
    plugin._dr_page_mapping = {"001": _index_dr_mock()}

    markdown = plugin._build_index_markdown(_index_file())

    assert "| ID | Date | Title | Status | Deciders |" in markdown


def test_build_index_markdown_returns_none_for_empty_mapping():
    plugin = _index_plugin()

    assert plugin._build_index_markdown(_index_file()) is None


def test_build_index_markdown_returns_none_when_only_template():
    plugin = _index_plugin()
    plugin._dr_page_mapping = {"000": _index_dr_mock(dr_id="000", is_template=True)}

    assert plugin._build_index_markdown(_index_file()) is None


def test_build_index_markdown_excludes_template():
    plugin = _index_plugin()
    plugin._dr_page_mapping = {
        "000": _index_dr_mock(dr_id="000", is_template=True),
        "001": _index_dr_mock(dr_id="001"),
    }

    rows = _index_rows(plugin._build_index_markdown(_index_file()))

    assert len(rows) == 1
    assert rows[0][0] == "001"


def test_build_index_markdown_sorts_by_id_numerically():
    plugin = _index_plugin()
    plugin._dr_page_mapping = {
        "10": _index_dr_mock(dr_id="10", title="10 - Tenth"),
        "2": _index_dr_mock(dr_id="2", title="2 - Second"),
        "1": _index_dr_mock(dr_id="1", title="1 - First"),
    }

    markdown = plugin._build_index_markdown(_index_file())

    assert [row[0] for row in _index_rows(markdown)] == ["1", "2", "10"]


def test_build_index_markdown_title_is_link_with_prefix_stripped():
    plugin = _index_plugin()
    plugin._dr_page_mapping = {
        "001": _index_dr_mock(
            dr_id="001",
            title="001 - Mechanism to validate mjml code",
            src_uri="adr/001-mechanism-to-validate-mjml-code.md",
        ),
    }

    markdown = plugin._build_index_markdown(_index_file())

    assert (
        "| [Mechanism to validate mjml code](001-mechanism-to-validate-mjml-code.md) |"
        in markdown
    )
    assert "001 - Mechanism" not in markdown


@pytest.mark.parametrize(
    ["dr_id", "filename", "expected_title"],
    [
        ("002", "002-Solution-for-preview", "Solution for preview"),
        ("001", "my-notes", "My notes"),
    ],
)
def test_build_index_markdown_title_falls_back_to_filename(
    dr_id, filename, expected_title
):
    """Records with no frontmatter title and no H1 are titled from the file name."""
    plugin = _index_plugin()
    dr = _index_dr_mock(dr_id=dr_id, title="")
    dr.file.name = filename
    plugin._dr_page_mapping = {dr_id: dr}

    markdown = plugin._build_index_markdown(_index_file())

    assert f"[{expected_title}](" in markdown


def test_build_index_markdown_quotes_link_for_special_characters():
    plugin = _index_plugin()
    plugin._dr_page_mapping = {
        "001": _index_dr_mock(dr_id="001", src_uri="adr/001 with space.md"),
    }

    markdown = plugin._build_index_markdown(_index_file())

    assert "](001%20with%20space.md)" in markdown


def test_build_index_markdown_escapes_table_breaking_characters():
    plugin = _index_plugin()
    plugin._dr_page_mapping = {
        "001": _index_dr_mock(
            dr_id="001",
            title="001 - Foo | Bar [baz]",
            deciders=["A | B", "C"],
        ),
    }

    markdown = plugin._build_index_markdown(_index_file())

    assert "[Foo \\| Bar \\[baz\\]](" in markdown
    assert "A \\| B, C" in markdown


def test_build_index_markdown_links_records_in_subfolders():
    plugin = _index_plugin()
    plugin._dr_page_mapping = {
        "001": _index_dr_mock(dr_id="001", src_uri="adr/nested/001-decision.md"),
    }

    markdown = plugin._build_index_markdown(_index_file())

    assert "](nested/001-decision.md)" in markdown


@pytest.mark.parametrize(
    ["deciders", "expected_cell"],
    [
        ([], ""),
        (["Alice"], "Alice"),
        (["Alice", "Bob"], "Alice, Bob"),
        (["A", "B", "C"], "A, B, C"),
        (["A", "B", "C", "D"], "A, B, C, ..."),
        (["A", "B", "C", "D", "E"], "A, B, C, ..."),
    ],
)
def test_build_index_markdown_deciders_truncation(deciders, expected_cell):
    plugin = _index_plugin()
    plugin._dr_page_mapping = {"001": _index_dr_mock(deciders=deciders)}

    markdown = plugin._build_index_markdown(_index_file())

    # id, date, title, status, deciders
    assert _index_rows(markdown)[0][4] == expected_cell


def test_build_index_markdown_no_ticket_column_without_prefix():
    plugin = _index_plugin()
    plugin._dr_page_mapping = {"001": _index_dr_mock(ticket="FOO-1")}

    markdown = plugin._build_index_markdown(_index_file())

    assert "Ticket" not in markdown
    assert "FOO-1" not in markdown


def test_build_index_markdown_ticket_column_linked_with_prefix():
    plugin = _index_plugin(ticket_url_prefix="https://jira.example.com")
    plugin._dr_page_mapping = {"001": _index_dr_mock(ticket="foo-1")}

    markdown = plugin._build_index_markdown(_index_file())

    assert "| Ticket |" in markdown
    assert "| [FOO-1](https://jira.example.com/foo-1) |" in markdown


def test_build_index_markdown_ticket_cell_empty_when_record_has_no_ticket():
    plugin = _index_plugin(ticket_url_prefix="https://jira.example.com")
    plugin._dr_page_mapping = {"001": _index_dr_mock(ticket=None)}

    # id, date, title, status, ticket, deciders
    assert _index_rows(plugin._build_index_markdown(_index_file()))[0][4] == ""


def test_build_index_markdown_renders_status_badge():
    plugin = _index_plugin()
    plugin._dr_page_mapping = {"001": _index_dr_mock(status="accepted")}

    markdown = plugin._build_index_markdown(_index_file())

    assert "background:#28a745" in markdown
    assert ">accepted</span>" in markdown


def test_build_index_markdown_unknown_status_falls_back_to_plain_text():
    plugin = _index_plugin()
    plugin._dr_page_mapping = {"001": _index_dr_mock(status="draft")}

    markdown = plugin._build_index_markdown(_index_file())

    assert "| draft |" in markdown


def test_build_index_markdown_formats_string_dates():
    """YAML keeps quoted dates as plain strings - the table must still render."""
    plugin = _index_plugin()
    dr = _index_dr_mock()
    dr.date = "2024-01-01"
    plugin._dr_page_mapping = {"001": dr}

    markdown = plugin._build_index_markdown(_index_file())

    assert "| 001 | 2024-01-01 |" in markdown


def test_on_files_appends_generated_index_file():
    plugin = _index_plugin(generate_index_page=True)
    config = MagicMock()
    files = Files(
        [
            File.generated(
                config,
                src_uri="adr/001-decision.md",
                content=_create_content(
                    "# ADR 001",
                    {"id": "001", "status": "accepted", "date": "2024-01-01"},
                ),
            ),
        ]
    )

    plugin.on_files(files, config=config)

    assert "adr/index.md" in [f.src_uri for f in files]
    index_file = next(f for f in files if f.src_uri == "adr/index.md")
    assert "| ID | Date | Title | Status | Deciders |" in index_file.content_string
    assert "001" in index_file.content_string
    # links must be source-relative so MkDocs can resolve and rewrite them
    assert "](001-decision.md)" in index_file.content_string
    assert "](adr/001-decision" not in index_file.content_string


def test_on_files_skips_index_generation_when_disabled():
    plugin = _index_plugin()
    config = MagicMock()
    files = Files(
        [
            File.generated(
                config,
                src_uri="adr/001-decision.md",
                content=_create_content(
                    "# ADR 001",
                    {"id": "001", "status": "accepted", "date": "2024-01-01"},
                ),
            ),
        ]
    )

    plugin.on_files(files, config=config)

    assert "adr/index.md" not in [f.src_uri for f in files]


def test_on_files_keeps_user_index_when_disabled():
    plugin = _index_plugin()
    config = MagicMock()
    files = Files(
        [File.generated(config, src_uri="adr/index.md", content="# My own index")]
    )

    plugin.on_files(files, config=config)

    [index_file] = [f for f in files if f.src_uri == "adr/index.md"]
    assert index_file.content_string == "# My own index"


def test_on_files_overrides_existing_index_when_enabled():
    plugin = _index_plugin(generate_index_page=True)
    config = MagicMock()
    files = Files(
        [
            File.generated(config, src_uri="adr/index.md", content="# My own index"),
            File.generated(
                config,
                src_uri="adr/001-decision.md",
                content=_create_content(
                    "# ADR 001",
                    {"id": "001", "status": "accepted", "date": "2024-01-01"},
                ),
            ),
        ]
    )

    plugin.on_files(files, config=config)

    index_files = [f for f in files if f.src_uri == "adr/index.md"]
    assert len(index_files) == 1
    assert "# My own index" not in index_files[0].content_string
    assert "| ID | Date | Title | Status | Deciders |" in index_files[0].content_string


def test_on_files_skips_index_when_only_template_exists():
    plugin = _index_plugin(generate_index_page=True)
    config = MagicMock()
    files = Files(
        [
            File.generated(
                config,
                src_uri="adr/000-template.md",
                content=_create_content(
                    "# Template",
                    {"id": "000", "status": "proposed", "date": "2024-01-01"},
                ),
            ),
        ]
    )

    plugin.on_files(files, config=config)

    assert "adr/index.md" not in [f.src_uri for f in files]


def test_on_files_clears_records_from_previous_build():
    """`mkdocs serve` reuses the plugin - deleted records must not linger."""
    plugin = _index_plugin(generate_index_page=True)
    plugin._dr_page_mapping = {"009": _index_dr_mock(dr_id="009")}
    config = MagicMock()
    files = Files(
        [
            File.generated(
                config,
                src_uri="adr/001-decision.md",
                content=_create_content(
                    "# ADR 001",
                    {"id": "001", "status": "accepted", "date": "2024-01-01"},
                ),
            ),
        ]
    )

    plugin.on_files(files, config=config)

    assert "009" not in plugin._dr_page_mapping
    assert "001" in plugin._dr_page_mapping


def test_on_files_generates_index_in_nested_decisions_folder():
    plugin = _index_plugin(
        decisions_folder="internal/adr", generate_index_page=True
    )
    config = MagicMock()
    files = Files(
        [
            File.generated(
                config,
                src_uri="internal/adr/001-decision.md",
                content=_create_content(
                    "# ADR 001",
                    {"id": "001", "status": "accepted", "date": "2024-01-01"},
                ),
            ),
        ]
    )

    plugin.on_files(files, config=config)

    assert "internal/adr/index.md" in [f.src_uri for f in files]
