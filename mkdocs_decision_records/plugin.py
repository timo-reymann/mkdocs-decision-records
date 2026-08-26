import json
import re
import os
from typing import Any, Generator

import frontmatter
from mkdocs.config import config_options
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import PluginError
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page

from mkdocs_decision_records._html_parser import BasicTextContentParser
from mkdocs_decision_records._markdown_utils import _list, _meta_table
from mkdocs_decision_records._model_meta import MetaModel
from mkdocs_decision_records._model_record import (
    NormalizedDecisionRecord,
    RawDecisionRecord,
    format_decision_record_display_id,
)

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


class InvalidMetaDataExcpetion(PluginError):
    def __init__(self, page: Page, errors: list[InvalidMetaDataError]):
        errors_lines = "\n".join(str(e) for e in errors)
        src_path = getattr(page, "src_path", None) or getattr(getattr(page, "file", None), "src_path", "unknown") if page else "unknown"
        self.message = f"Invalid metadata for {src_path}: {errors_lines}"


def _normalize_id_for_comparison(value: Any) -> Any:
    """Normalize a raw frontmatter id for equality comparison.

    MkDocs' own frontmatter parser resolves a leading-zero id like ``008``
    or ``009`` as a plain string (it looks like octal, but ``8``/``9`` are
    not valid octal digits), while ``000``-``007`` resolve to ``int``. Without
    normalization, comparing those inconsistent raw types against the
    zero-padded display id can produce false positives/negatives.
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        return value


def _ensure_page_is_unique(dr_id, files, page):
    normalized_dr_id = _normalize_id_for_comparison(dr_id)
    same_id_pages = [
        f.src_path
        for f in files.documentation_pages()
        if f.page is not None
        and f.page is not page
        and f.page.meta
        and _normalize_id_for_comparison(f.page.meta.get("id", None))
        == normalized_dr_id
    ]
    if len(same_id_pages) > 0:
        pages = ", ".join(same_id_pages)
        raise InvalidMetaDataError(page, "id", f"Uses same id as {pages}")


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
    _dr_page_mapping: dict[str, NormalizedDecisionRecord] = {}

    def _parse_decision_record_page(
        self, file: File, meta: frontmatter.Post | None = None
    ) -> NormalizedDecisionRecord:
        raw = RawDecisionRecord.from_file(file, meta)
        dr, errors = raw.validate(
            validate_id_len=self.validate_id_length,
            padded_id_len=self.id_length,
            required_deciders_count=self.required_deciders_count,
        )
        if errors:
            raise InvalidMetaDataExcpetion(file.page, errors)
        assert dr is not None
        return dr

    def _generate_index(self) -> Generator[dict[str, str | list], Any, None]:
        for dr in self._dr_page_mapping.values():
            if dr.is_template():
                continue

            dr_index = {
                "id": dr.id,
                "date": dr.date.isoformat(),
                "title": dr.title,
                "status": dr.status,
            }

            if (content := dr.file.page.content) is not None:
                html_parser = BasicTextContentParser()
                html_parser.feed(content)
                html_parser.close()

                content_sections = []
                for section in html_parser.data:
                    if not section.is_excluded():
                        content_sections.append(
                            {
                                "title": "".join(section.title).strip(),
                                "text": "\n".join(section.text).strip(),
                            }
                        )
                dr_index["toc"] = dr.file.page.toc
                dr_index["sections"] = content_sections

            if dr.status == "superseded" and dr.superseded_by:
                dr_index["superseded_by"] = dr.superseded_by

            yield dr_index

    def on_post_build(self, *, config: MkDocsConfig) -> None:
        dr_index = json.dumps(list(self._generate_index()), default=str)
        index_file = os.path.join(config.site_dir, "decision_index.json")
        with open(index_file, "w") as f:
            f.write(dr_index)

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

            if self._is_section_index(doc.src_uri):
                continue

            parsed_frontmatter = frontmatter.loads(doc.content_string)
            dr = self._parse_decision_record_page(doc, parsed_frontmatter)
            self._dr_page_mapping[dr.id] = dr

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

        # index.md is a section overview page (e.g. an awesome-pages folder
        # landing page), not a decision record — it must not be matched by
        # the `id: 0` template sentinel below.
        if self._is_section_index(page.file.src_uri):
            return markdown

        dr = self._parse_decision_record_page(page.file)

        # set page title
        page.title = dr.title

        if dr.is_template():
            return markdown

        _ensure_page_is_unique(dr.id, files, page)

        meta_model = MetaModel()
        meta_model.add(
            key="Status",
            value=self._create_status_badge(dr),
        )
        meta_model.add(
            key="Date",
            value=dr.date,
        )

        if len(dr.deciders) > 0:
            meta_model.add(
                key="Deciders" if dr.has_multiple_deciders else "Decider",
                value="\n".join(_list(dr.deciders))
                if len(dr.deciders) > 1
                else dr.deciders[0],
            )

        if dr.ticket is not None:
            meta_model.add(
                key="Ticket",
                value=self._ticket_text(dr.ticket),
            )

        if dr.status == "superseded":
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

            if (
                format_decision_record_display_id(
                    superseded_by_id, padded_len=self.id_length
                )
                not in self._dr_page_mapping
            ):
                raise InvalidMetaDataError(
                    page,
                    "superseded_by",
                    "Decision records with identifier %s has not been found"
                    % superseded_by,
                )

            meta_model.add(
                key="Superseded by",
                value=f"<a href='{self._dr_page_mapping[format_decision_record_display_id(superseded_by_id, padded_len=self.id_length)].file.url_relative_to(page.file)}'>{superseded_by}</a>",
            )

        meta_info = "\n".join(_meta_table(meta_model.get_all()))

        return f"{dr.title}\n===\n{meta_info}\n{markdown}"

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

    @staticmethod
    def _is_section_index(src_uri: str) -> bool:
        return os.path.basename(src_uri).lower() == "index.md"

    def _create_status_badge(self, dr: NormalizedDecisionRecord):
        status_color = self.lifecycles.get(dr.status, None)
        if status_color is None:
            raise InvalidMetaDataError(dr.file.page, "status", f"Invalid status {dr.status}")

        return (
            f"<span style='color: white;background:{status_color};padding:.4em;border-radius:8px;font-size:100%;'>"
            f"{dr.status}"
            f"</span>"
        )

    def _ticket_text(self, ticket: str):
        if self.config.get(CONFIG_TICKET_URL_PREFIX) is not None:
            return f"<a href='{self.config.get(CONFIG_TICKET_URL_PREFIX)}/{ticket}'>{ticket.upper()}</a>"

        return ticket.upper()
