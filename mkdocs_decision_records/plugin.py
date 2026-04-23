import re
import os

import frontmatter
from mkdocs.config import config_options
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import PluginError
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page

from mkdocs_decision_records._markdown_utils import _list, _meta_table

# ProperDocs replacement warning
try:
    import properdocs.replacement_warning

    properdocs.replacement_warning.setup()
except ImportError:
    # properdocs not installed, skip warning
    pass

CONFIG_DECISIONS_FOLDER_KEY = "decisions_folder"
CONFIG_TICKET_URL_PREFIX = "ticket_url_prefix"

CONFIG_LIFECYCLE_COLORS_KEY = "lifecycle_stages"
CONFIG_DECISIONS_FOLDER_DEFAULT = "adr"

CONFIG_DECISION_ID_LENGTH_KEY = "decision_id_length"
CONFIG_DECISION_ID_LENGTH_DEFAULT = 3
CONFIG_DECISION_ID_LENGTH_VALIDATE_KEY = "validate_id_length"
CONFIG_DECISION_ID_LENGTH_VALIDATE_DEFAULT = False


def _normalize_decisions_folder(folder: str) -> str:
    """Normalize decisions_folder to use forward slashes and no trailing slash.

    This ensures OS-independent path matching by converting Windows-style
    backslashes to forward slashes and removing any trailing slashes.
    """
    return folder.replace("\\", "/").rstrip("/")


CONFIG_REQUIRED_DECIDERS_COUNT_KEY = "required_deciders_count"
CONFIG_REQUIRED_DECIDERS_COUNT_DEFAULT = 1

DR_NUM = re.compile(r"(?:[a-zA-Z\-]+)?(\d+)")

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
        self.message = (
            f"Invalid metadata for field '{field}' in {page.file.src_path}: {message}"
        )


def _require_meta(page: Page, field: str) -> any:
    val = page.meta.get(field, None)
    if val is None:
        raise InvalidMetaDataError(page, field, "Required, but not set.")
    return val


class DecisionRecordsPlugin(BasePlugin):
    config_scheme = (
        (
            CONFIG_DECISIONS_FOLDER_KEY,
            config_options.Type(str, default=CONFIG_DECISIONS_FOLDER_DEFAULT),
        ),
        (CONFIG_TICKET_URL_PREFIX, config_options.Type(str, default=None)),
        (
            CONFIG_LIFECYCLE_COLORS_KEY,
            config_options.Type(dict, default=DEFAULT_LIFECYCLE_COLORS),
        ),
        (
            CONFIG_REQUIRED_DECIDERS_COUNT_KEY,
            config_options.Type(int, default=CONFIG_REQUIRED_DECIDERS_COUNT_DEFAULT),
        ),
        (
            CONFIG_DECISION_ID_LENGTH_KEY,
            config_options.Type(int, default=CONFIG_DECISION_ID_LENGTH_DEFAULT),
        ),
        (
            CONFIG_DECISION_ID_LENGTH_VALIDATE_KEY,
            config_options.Type(
                bool, default=CONFIG_DECISION_ID_LENGTH_VALIDATE_DEFAULT
            ),
        ),
    )
    _dr_page_mapping: dict[int | str, File] = {}

    def on_files(self, files: Files, /, *, config: MkDocsConfig) -> Files | None:
        docs_pages = files.documentation_pages()
        decisions_folder = _normalize_decisions_folder(
            self.config.get(
                CONFIG_DECISIONS_FOLDER_KEY, CONFIG_DECISIONS_FOLDER_DEFAULT
            )
        )
        for doc in docs_pages:
            # Only process files in the decisions folder
            # Use src_uri instead of src_path for OS-independent path matching
            if not doc.src_uri.startswith(decisions_folder):
                continue
            parsed_frontmatter = frontmatter.loads(doc.content_string)
            dr_id = parsed_frontmatter.get("id", None)
            if dr_id is None:
                continue
            dr_id_int = int(dr_id)
            if self.validate_id_length and not self._id_matches_length(dr_id):
                raise PluginError(
                    f"ID in {doc.src_uri} must be {self.id_length} digits long, got '{dr_id}'"
                )
            self._dr_page_mapping[dr_id_int] = doc

    def on_page_markdown(
        self, markdown: str, page: Page, config: MkDocsConfig, files: Files
    ):
        # Use src_uri instead of src_path for OS-independent path matching
        decisions_folder = _normalize_decisions_folder(
            self.config.get(
                CONFIG_DECISIONS_FOLDER_KEY, CONFIG_DECISIONS_FOLDER_DEFAULT
            )
        )
        if not page.file.src_uri.startswith(decisions_folder):
            return markdown

        title = page.meta.get("title", None) or page.title
        dr_id = _require_meta(page, "id")

        if self.validate_id_length and not self._id_matches_length(dr_id):
            raise InvalidMetaDataError(
                page,
                "id",
                f"ID must be {self.id_length} digits long, got '{dr_id}'",
            )

        if dr_id == 0:
            page.title = f"{self._id_format(0)} - Template"
            return markdown

        self._ensure_page_is_unique(dr_id, files, page)

        meta = [
            ("Status", self._create_status_badge(page)),
            ("Date", _require_meta(page, "date")),
        ]

        deciders = page.meta.get("deciders", [])
        if len(deciders) < self.required_deciders_count:
            raise InvalidMetaDataError(
                page,
                "deciders",
                f"At least {self.required_deciders_count} deciders are required for a decision",
            )
        elif len(deciders) > 0:
            meta.append(
                (
                    "Deciders" if len(deciders) > 1 else "Decider",
                    "\n".join(_list(deciders)) if len(deciders) > 1 else deciders[0],
                )
            )

        ticket = page.meta.get("ticket", None)
        if ticket is not None:
            meta.append(
                (
                    "Ticket",
                    self._ticket_text(ticket),
                )
            )

        status = _require_meta(page, "status")
        if status == "superseded":
            superseded_by = page.meta.get("superseded_by", None)
            if superseded_by is None:
                raise InvalidMetaDataError(
                    page,
                    "superseded_by",
                    "When setting an ADR to superseded you need to set superseded_by to an ADR id.",
                )

            superseded_by_id = superseded_by
            if match := DR_NUM.match(str(superseded_by)):
                superseded_by_id = int(match.group(1))

            if self.validate_id_length and not self._id_matches_length(
                superseded_by_id
            ):
                raise InvalidMetaDataError(
                    page,
                    "superseded_by",
                    f"ID must be {self.id_length} digits long, got '{superseded_by_id}'",
                )

            if isinstance(superseded_by, int):
                superseded_by = self._id_format(superseded_by)

            if superseded_by_id not in self._dr_page_mapping:
                raise InvalidMetaDataError(
                    page,
                    "superseded_by",
                    "Decision records with identifier %s has not been found"
                    % superseded_by,
                )

            meta.append(
                (
                    "Superseded by",
                    f"<a href='{self._dr_page_mapping[superseded_by_id].url_relative_to(page.file)}'>{superseded_by}</a>",
                )
            )

        meta_info = "\n".join(_meta_table(meta))

        title_has_id = re.match(rf"\d{{{self.id_length}}},.*", title)
        header = title if title_has_id else f"{self._id_format(dr_id)} - {title}"
        page.title = header

        return f"{header}\n===\n{meta_info}\n{markdown}"

    @property
    def lifecycles(self) -> dict[str, str]:
        configured_lifecycle_colors = self.config.get(CONFIG_LIFECYCLE_COLORS_KEY, {})
        return {
            **DEFAULT_LIFECYCLE_COLORS,
            **configured_lifecycle_colors,
        }

    @property
    def required_deciders_count(self):
        return self.config.get(
            CONFIG_REQUIRED_DECIDERS_COUNT_KEY, CONFIG_REQUIRED_DECIDERS_COUNT_DEFAULT
        )

    @property
    def id_length(self):
        return self.config.get(
            CONFIG_DECISION_ID_LENGTH_KEY, CONFIG_DECISION_ID_LENGTH_DEFAULT
        )

    @property
    def validate_id_length(self):
        return self.config.get(
            CONFIG_DECISION_ID_LENGTH_VALIDATE_KEY,
            CONFIG_DECISION_ID_LENGTH_VALIDATE_DEFAULT,
        )

    def _id_format(self, id_val: int | str) -> str:
        id_int = int(id_val)
        return f"{id_int:0{self.id_length}d}"

    def _id_matches_length(self, id_val: int | str) -> bool:
        if isinstance(id_val, int):
            return len(str(id_val)) <= self.id_length
        return len(id_val) == self.id_length

    def _ensure_page_is_unique(self, dr_id, files, page):
        same_id_pages = [
            p.src_path
            for p in files.documentation_pages()
            if p is not page.file
            and p.page
            and p.page.meta
            and p.page.meta.get("id", None) == dr_id
        ]
        if len(same_id_pages) > 0:
            pages = ", ".join(same_id_pages)
            raise InvalidMetaDataError(page, "id", f"Uses same id as {pages}")

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

    def _ticket_text(self, ticket: str):
        if self.config.get(CONFIG_TICKET_URL_PREFIX) is not None:
            return f"<a href='{self.config.get(CONFIG_TICKET_URL_PREFIX)}/{ticket}'>{ticket.upper()}</a>"

        return ticket.upper()
