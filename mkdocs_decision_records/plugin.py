import re
from collections.abc import Generator
from typing import Any

from mkdocs.config import config_options
from mkdocs.config.base import ConfigErrors, ConfigWarnings
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import PluginError
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page

CONFIG_DECISIONS_FOLDER_KEY = "decisions_folder"
CONFIG_TICKET_URL_PREFIX = "ticket_url_prefix"
CONFIG_DECISIONS_FOLDER_DEFAULT = "adr"
DR_TITLE_WITH_NUM = re.compile(r'\d{3,}.*')
DEFAULT_LIFECYCLE_COLORS = {
    "accepted": "green",
}


class InvalidMetaDataError(PluginError):
    def __init__(self, page: Page, field: str, message: str):
        self.field = field
        self.raw_message = message
        self.message = f"Invalid metadata for field '{field}' in {page.file.src_path}: {message}"


def _require_meta(page: Page, field: str) -> any:
    val = page.meta.get(field, None)
    if val is None:
        raise InvalidMetaDataError(page, field, "Required, but not set.")
    return val


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


class DecisionRecordsPlugin(BasePlugin):
    config_scheme = (
        (CONFIG_DECISIONS_FOLDER_KEY, config_options.DocsDir(exists=True)),
        (CONFIG_TICKET_URL_PREFIX, config_options.Type(str, default=None))
    )

    ticket_base_url: str | None = None
    decisions_folder: str = None

    def _store_config(self, config):
        self.ticket_base_url = config.get(CONFIG_TICKET_URL_PREFIX, None)
        self.decisions_folder = config.get(CONFIG_DECISIONS_FOLDER_KEY, CONFIG_DECISIONS_FOLDER_DEFAULT)

    def load_config(
            self,
            options: dict[str, Any],
            config_file_path: str | None = None,
    ) -> tuple[ConfigErrors, ConfigWarnings]:
        self._store_config(options)
        return [], []

    def on_page_markdown(self, markdown: str, page: Page, config: MkDocsConfig, files: Files):
        if not page.file.src_path.startswith(self.decisions_folder):
            return markdown

        title = page.meta.get("title", None) or page.title
        dr_id = _require_meta(page, "id")

        status = _require_meta(page, "status")
        status_color = DEFAULT_LIFECYCLE_COLORS.get(status, None)
        if status_color is None:
            status_badge = status
        else:
            status_badge = f"<span style='color: white;background:{status_color};padding:.4em;border-radius:8px;font-size:100%;'>{status}</span>"

        meta = [
            ("Status", status_badge),
            ("Date", _require_meta(page, "date")),
        ]

        deciders = page.meta.get("deciders", None)
        if deciders is not None:
            meta.append((
                "Deciders",
                "\n".join(_list(deciders)),
            ))

        ticket = page.meta.get("ticket", None)
        if ticket is not None:
            if self.ticket_base_url is not None:
                ticket_text = f"<a href='{self.ticket_base_url}/{ticket}'>{ticket.upper()}</a>"
            else:
                ticket_text = ticket.upper()

            meta.append((
                "Ticket",
                ticket_text,
            ))

        table = "\n".join(_meta_table(meta))

        header = title if DR_TITLE_WITH_NUM.match(title) else f"{dr_id:03d} - {title}"
        page.title = header
        return f"{header}\n=== \n{table}\n{markdown}"
