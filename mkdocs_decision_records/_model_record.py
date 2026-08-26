import dataclasses
import datetime

from frontmatter import Post
from mkdocs.structure.files import File
from mkdocs.structure.pages import Page


class InvalidMetaDataError:
    def __init__(self, page: Page, field: str, message: str):
        self.field = field
        src_path = getattr(page, "src_path", None) or getattr(getattr(page, "file", None), "src_path", "unknown")
        self.message = (
            f"Invalid metadata for field '{field}' in {src_path}: {message}"
        )

    def __str__(self) -> str:
        return self.message

@dataclasses.dataclass(frozen=True)
class NormalizedDecisionRecord:
    file: File
    id: str
    title: str | None
    status: str
    date: datetime.date
    deciders: list[str]
    superseded_by: str | None = None
    ticket: str | None = None

    def is_template(self):
        return int(self.id) == 0

    @property
    def has_multiple_deciders(self):
        return len(self.deciders) > 1


@dataclasses.dataclass
class RawDecisionRecord:
    _file: File
    _id: int | str | None
    title: str | None
    status: str | None
    superseded_by: int | None = None
    date: datetime.date | None = None
    deciders: list[str] | None = None
    ticket: str | None = None

    @staticmethod
    def from_file(file: File, meta: Post | None) -> "RawDecisionRecord":
        if meta:
            meta = meta.to_dict()
        else:
            meta = file.page.meta
        page_title = file.page.title if file.page is not None else None
        return RawDecisionRecord(
            _file=file,
            _id=meta.get("id", None),
            title=meta.get("title", None) or page_title,
            status=meta.get("status", None) or "",
            superseded_by=meta.get("superseded_by", None),
            date=meta.get("date", None),
            deciders=meta.get("deciders", None),
            ticket=meta.get("ticket", None),
        )

    def display_id(self, padded_len: int) -> str:
        return format_decision_record_display_id(self._id, padded_len)

    def validate(
        self,
        validate_id_len: bool,
        padded_id_len: int,
        required_deciders_count: int,
    ) -> tuple[NormalizedDecisionRecord | None, list[InvalidMetaDataError]]:
        errors = []

        if self._id is None:
            errors.append(
                InvalidMetaDataError(self._file, "id", "Required, but not set.")
            )

        if (
            validate_id_len
            and self._id is not None
            and len(str(self._id)) != padded_id_len
        ):
            errors.append(
                InvalidMetaDataError(
                    self._file,
                    "id",
                    f"Expected length {padded_id_len}, but got {len(str(self._id))}.",
                )
            )

        if self.status is None or self.status == "":
            errors.append(
                InvalidMetaDataError(self._file, "status", "Required, but not set.")
            )

        if self.date is None or self.date == "":
            errors.append(
                InvalidMetaDataError(self._file, "date", "Required, but not set.")
            )

        if self.deciders and len(self.deciders) < required_deciders_count:
            errors.append(
                InvalidMetaDataError(
                    self._file,
                    "deciders",
                    f"At least {required_deciders_count} deciders are required for a decision",
                )
            )

        if len(errors) > 0:
            return None, errors

        if self.title:
            display_id = self.display_id(padded_id_len)
            for prefix in (display_id, str(self._id)):
                if self.title.startswith(prefix):
                    self.title = self.title[len(prefix) :].lstrip(" -_:.")
                    break

            self.title = f"{display_id} - {self.title}"

            if int(display_id) == 0:
                self.title = f"{display_id} - Template"

        if self.status == "superseded" and self.superseded_by is not None:
            superseded_by_id = int(self.superseded_by)
            superseded_by = format_decision_record_display_id(superseded_by_id, padded_id_len)
        else:
            superseded_by = None

        # At this point we have a valid decision record
        assert self.status is not None
        assert self.date is not None
        assert self._file is not None
        return NormalizedDecisionRecord(
            file=self._file,
            id=self.display_id(padded_id_len),
            superseded_by=superseded_by,
            title=self.title,
            status=self.status,
            date=self.date,
            deciders=self.deciders or [],
            ticket=self.ticket,
        ), []


def format_decision_record_display_id(_id: int | None, padded_len: int) -> str:
    if _id is None:
        id_int = 0
    else:
        id_int = int(_id)

    return f"{id_int:0{padded_len}d}"


def _require_meta(
    page: Page, field: str
) -> str | int | datetime.datetime | InvalidMetaDataError:
    val = page.meta.get(field, None)
    if val is None:
        return InvalidMetaDataError(page, field, "Required, but not set.")
    return val


def _id_matches_length(id_val: int | str, id_length: int) -> bool:
    if isinstance(id_val, int):
        return len(str(id_val)) <= id_length
    return len(id_val) == id_length
