import re

from mkdocs.config import config_options
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import PluginError
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page

from mkdocs_decision_records._markdown_utils import _list, _meta_table

CONFIG_DECISIONS_FOLDER_KEY = "decisions_folder"
CONFIG_TICKET_URL_PREFIX = "ticket_url_prefix"

CONFIG_LIFECYCLE_COLORS_KEY = "lifecycle_stages"
CONFIG_DECISIONS_FOLDER_DEFAULT = "adr"

CONFIG_REQUIRED_DECIDERS_COUNT_KEY = "required_deciders_count"
CONFIG_REQUIRED_DECIDERS_COUNT_DEFAULT = 1

DR_TITLE_WITH_NUM = re.compile(r'\d{3,}.*')

DEFAULT_LIFECYCLE_COLORS = {
    "accepted": "#28a745",
    "proposed": "gray",
    "rejected": "#dc3545",
    "deprecated": "#6c757d",
    "superseded": "#17a2b8",
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


class DecisionRecordsPlugin(BasePlugin):
    config_scheme = (
        (CONFIG_DECISIONS_FOLDER_KEY, config_options.Type(str, default=CONFIG_DECISIONS_FOLDER_DEFAULT)),
        (CONFIG_TICKET_URL_PREFIX, config_options.Type(str, default=None)),
        (CONFIG_LIFECYCLE_COLORS_KEY, config_options.Type(dict, default=DEFAULT_LIFECYCLE_COLORS)),
        (CONFIG_REQUIRED_DECIDERS_COUNT_KEY, config_options.Type(int, default=CONFIG_REQUIRED_DECIDERS_COUNT_DEFAULT))
    )

    def on_page_markdown(self, markdown: str, page: Page, config: MkDocsConfig, files: Files):
        if not page.file.src_path.startswith(self.config.get(CONFIG_DECISIONS_FOLDER_KEY)):
            return markdown

        title = page.meta.get("title", None) or page.title
        dr_id = _require_meta(page, "id")

        if dr_id == 0:
            page.title = "000 - Template"
            return markdown

        meta = [
            ("Status", self._create_status_badge(page)),
            ("Date", _require_meta(page, "date")),
        ]

        deciders = page.meta.get("deciders", [])
        if len(deciders) < self.required_deciders_count:
            raise InvalidMetaDataError(page, "deciders",
                                       f"At least {self.required_deciders_count} deciders are required for a decision")
        elif len(deciders) > 0:
            meta.append((
                "Deciders" if len(deciders) > 1 else "Decider",
                "\n".join(_list(deciders)) if len(deciders) > 1 else deciders[0],
            ))

        ticket = page.meta.get("ticket", None)
        if ticket is not None:
            if self.config.get(CONFIG_TICKET_URL_PREFIX) is not None:
                ticket_text = f"<a href='{self.config.get(CONFIG_TICKET_URL_PREFIX)}/{ticket}'>{ticket.upper()}</a>"
            else:
                ticket_text = ticket.upper()

            meta.append((
                "Ticket",
                ticket_text,
            ))

        meta_info = "\n".join(_meta_table(meta))

        header = title if DR_TITLE_WITH_NUM.match(title) else f"{dr_id:03d} - {title}"
        page.title = header

        return (
            f"{header}\n"
            f"===\n"
            f"{meta_info}\n"
            f"{markdown}"
        )

    @property
    def lifecycles(self) -> dict[str, str]:
        configured_lifecycle_colors = self.config.get(CONFIG_LIFECYCLE_COLORS_KEY, None)
        return {
            **DEFAULT_LIFECYCLE_COLORS,
            **configured_lifecycle_colors,
        }

    @property
    def required_deciders_count(self):
        return self.config.get(CONFIG_REQUIRED_DECIDERS_COUNT_KEY, CONFIG_REQUIRED_DECIDERS_COUNT_DEFAULT)

    def _create_status_badge(self, page):
        status = _require_meta(page, "status")

        status_color = self.lifecycles.get(status, None)
        if status_color is None:
            raise InvalidMetaDataError(page, "status", f"Invalid status {status}")

        return (
            f"<span style='color: white;background:{status_color};padding:.4em;border-radius:8px;font-size:100%;'>"
            f"{status}"
            f"</span>"
        )
