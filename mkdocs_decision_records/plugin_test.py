import pytest
from unittest.mock import MagicMock, patch
from mkdocs_decision_records.plugin import CONFIG_DECISIONS_FOLDER_KEY, CONFIG_TICKET_URL_PREFIX, DecisionRecordsPlugin, \
    InvalidMetaDataError

def test_on_page_markdown():
    plugin = DecisionRecordsPlugin()
    page = MagicMock()
    page.file.src_path = 'adr/decision.md'
    page.meta = {'id': 1, 'date': '2021-12-13', 'deciders': ['decider1', 'decider2'], 'status': 'accepted'}
    page.title = 'Decision 1'
    files = MagicMock()
    markdown = 'This is a decision record.'
    result = plugin.on_page_markdown(markdown, page, {}, files)
    assert 'Decision 1' in result

def test_lifecycles():
    plugin = DecisionRecordsPlugin()
    assert isinstance(plugin.lifecycles, dict)

def test_required_deciders_count():
    plugin = DecisionRecordsPlugin()
    assert isinstance(plugin.required_deciders_count, int)

def test_create_status_badge():
    plugin = DecisionRecordsPlugin()
    page = MagicMock()
    page.meta = {'status': 'accepted'}
    result = plugin._create_status_badge(page)
    assert 'accepted' in result

def test_invalid_metadata_error():
    plugin = DecisionRecordsPlugin()
    page = MagicMock()
    page.file.src_path = 'adr/decision.md'
    page.meta = {'id': 1, 'date': '2021-12-13', 'deciders': []}
    page.title = 'Decision 1'
    files = MagicMock()
    files.documentation_pages.return_value = []
    markdown = 'This is a decision record.'
    with pytest.raises(InvalidMetaDataError):
        plugin.on_page_markdown(markdown, page, {}, files)

def test_ticket_text():
    plugin = DecisionRecordsPlugin()
    assert plugin._ticket_text('JIRA-1234') == 'JIRA-1234'

    plugin.config[CONFIG_TICKET_URL_PREFIX] = 'https://jira.company.com'
    assert plugin._ticket_text('JIRA-1234') == "<a href='https://jira.company.com/JIRA-1234'>JIRA-1234</a>"