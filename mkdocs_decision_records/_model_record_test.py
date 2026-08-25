import datetime
from unittest.mock import MagicMock

import pytest

from mkdocs_decision_records._model_record import (
    NormalizedDecisionRecord,
    RawDecisionRecord,
    _id_matches_length,
    format_decision_record_display_id,
)


def test_format_id_basic_padded():
    assert format_decision_record_display_id(1, 3) == "001"


def test_format_id_already_full_length():
    assert format_decision_record_display_id(123, 3) == "123"


def test_format_id_zero():
    assert format_decision_record_display_id(0, 3) == "000"


def test_format_id_none_treated_as_zero():
    assert format_decision_record_display_id(None, 3) == "000"


def test_format_id_longer_id():
    assert format_decision_record_display_id(12345, 3) == "12345"


def test_format_id_four_digit_padded():
    assert format_decision_record_display_id(42, 4) == "0042"


def test_format_id_string_converted():
    assert format_decision_record_display_id("5", 3) == "005"


def test_id_matches_length_int_within():
    assert _id_matches_length(12, 3) is True


def test_id_matches_length_int_equal():
    assert _id_matches_length(123, 3) is True


def test_id_matches_length_int_exceeds():
    assert _id_matches_length(1234, 3) is False


def test_id_matches_length_string_exact():
    assert _id_matches_length("123", 3) is True


def test_id_matches_length_string_wrong():
    assert _id_matches_length("12", 3) is False


def test_id_matches_length_string_too_long():
    assert _id_matches_length("1234", 3) is False


def _make_record(id_str="001", status="accepted", deciders=None):
    file = MagicMock()
    return NormalizedDecisionRecord(
        file=file,
        id=id_str,
        title="Test Record",
        status=status,
        date=datetime.date(2024, 1, 1),
        deciders=deciders or ["Alice"],
    )


def test_normalized_is_template_true():
    record = _make_record(id_str="000")
    assert record.is_template() is True


def test_normalized_is_template_false():
    record = _make_record(id_str="001")
    assert record.is_template() is False


def test_normalized_has_multiple_deciders_true():
    record = _make_record(deciders=["Alice", "Bob"])
    assert record.has_multiple_deciders is True


def test_normalized_has_multiple_deciders_false():
    record = _make_record(deciders=["Alice"])
    assert record.has_multiple_deciders is False


def test_normalized_has_multiple_deciders_empty():
    record = _make_record(deciders=[])
    assert record.has_multiple_deciders is False


def test_normalized_frozen():
    record = _make_record()
    with pytest.raises(AttributeError):
        record.id = "999"


def _make_file(meta=None, page_title="Page Title"):
    file = MagicMock()
    file.page.meta = meta or {}
    file.page.title = page_title
    return file


def test_raw_from_file_with_post():
    import frontmatter

    file = _make_file()
    post = frontmatter.Post(
        "Content",
        id=1,
        title="Test",
        status="accepted",
        date=datetime.date(2024, 1, 1),
    )
    raw = RawDecisionRecord.from_file(file, post)
    assert raw._id == 1
    assert raw.title == "Test"
    assert raw.status == "accepted"


def test_raw_from_file_without_post():
    file = _make_file(meta={
        "id": 42,
        "title": "From Meta",
        "status": "proposed",
        "date": datetime.date(2024, 6, 15),
        "deciders": ["Alice"],
        "ticket": "JIRA-123",
        "superseded_by": 1,
    })
    raw = RawDecisionRecord.from_file(file, None)
    assert raw._id == 42
    assert raw.title == "From Meta"
    assert raw.status == "proposed"
    assert raw.deciders == ["Alice"]
    assert raw.ticket == "JIRA-123"
    assert raw.superseded_by == 1


def test_raw_from_file_falls_back_to_page_title():
    file = _make_file(meta={"id": 1, "status": "accepted", "date": datetime.date(2024, 1, 1)})
    raw = RawDecisionRecord.from_file(file, None)
    assert raw.title == "Page Title"


def test_raw_display_id():
    file = _make_file()
    raw = RawDecisionRecord(_file=file, _id=5, title="T", status="s", date=datetime.date(2024, 1, 1))
    assert raw.display_id(3) == "005"


def test_validate_missing_id():
    file = _make_file()
    raw = RawDecisionRecord(_file=file, _id=None, title="T", status="accepted", date=datetime.date(2024, 1, 1))
    dr, errors = raw.validate(validate_id_len=False, padded_id_len=3, required_deciders_count=1)
    assert dr is None
    assert any("id" in e.field for e in errors)


def test_validate_missing_status():
    file = _make_file()
    raw = RawDecisionRecord(_file=file, _id=1, title="T", status=None, date=datetime.date(2024, 1, 1))
    dr, errors = raw.validate(validate_id_len=False, padded_id_len=3, required_deciders_count=1)
    assert dr is None
    assert any("status" in e.field for e in errors)


def test_validate_missing_date():
    file = _make_file()
    raw = RawDecisionRecord(_file=file, _id=1, title="T", status="accepted", date=None)
    dr, errors = raw.validate(validate_id_len=False, padded_id_len=3, required_deciders_count=1)
    assert dr is None
    assert any("date" in e.field for e in errors)


def test_validate_too_few_deciders():
    file = _make_file()
    raw = RawDecisionRecord(
        _file=file, _id=1, title="T", status="accepted",
        date=datetime.date(2024, 1, 1), deciders=["Alice"],
    )
    dr, errors = raw.validate(validate_id_len=False, padded_id_len=3, required_deciders_count=2)
    assert dr is None
    assert any("deciders" in e.field for e in errors)


def test_validate_id_length_mismatch():
    file = _make_file()
    raw = RawDecisionRecord(_file=file, _id=1234, title="T", status="accepted", date=datetime.date(2024, 1, 1))
    dr, errors = raw.validate(validate_id_len=True, padded_id_len=3, required_deciders_count=1)
    assert dr is None
    assert any("id" in e.field for e in errors)


def test_validate_success():
    file = _make_file()
    raw = RawDecisionRecord(
        _file=file, _id=1, title="My Decision", status="accepted",
        date=datetime.date(2024, 1, 1), deciders=["Alice"],
    )
    dr, errors = raw.validate(validate_id_len=False, padded_id_len=3, required_deciders_count=1)
    assert errors == []
    assert dr is not None
    assert dr.id == "001"
    assert dr.title == "001 - My Decision"
    assert dr.status == "accepted"
    assert dr.deciders == ["Alice"]


def test_validate_strips_id_prefix_from_title():
    file = _make_file()
    raw = RawDecisionRecord(
        _file=file, _id=1, title="001 - My Decision", status="accepted",
        date=datetime.date(2024, 1, 1), deciders=["Alice"],
    )
    dr, errors = raw.validate(validate_id_len=False, padded_id_len=3, required_deciders_count=1)
    assert errors == []
    assert dr.title == "001 - My Decision"


def test_validate_template_title():
    file = _make_file()
    raw = RawDecisionRecord(
        _file=file, _id=0, title="Template", status="proposed",
        date=datetime.date(2024, 1, 1), deciders=["Alice"],
    )
    dr, errors = raw.validate(validate_id_len=False, padded_id_len=3, required_deciders_count=1)
    assert errors == []
    assert dr.title == "000 - Template"
    assert dr.is_template()


def test_validate_superseded():
    file = _make_file()
    raw = RawDecisionRecord(
        _file=file, _id=2, title="Decision 2", status="superseded",
        date=datetime.date(2024, 1, 1), deciders=["Alice"], superseded_by=1,
    )
    dr, errors = raw.validate(validate_id_len=False, padded_id_len=3, required_deciders_count=1)
    assert errors == []
    assert dr.superseded_by == "001"


def test_validate_ticket_preserved():
    file = _make_file()
    raw = RawDecisionRecord(
        _file=file, _id=1, title="T", status="accepted",
        date=datetime.date(2024, 1, 1), deciders=["Alice"], ticket="JIRA-123",
    )
    dr, errors = raw.validate(validate_id_len=False, padded_id_len=3, required_deciders_count=1)
    assert dr.ticket == "JIRA-123"


def test_validate_empty_status_treated_as_missing():
    file = _make_file()
    raw = RawDecisionRecord(_file=file, _id=1, title="T", status="", date=datetime.date(2024, 1, 1))
    dr, errors = raw.validate(validate_id_len=False, padded_id_len=3, required_deciders_count=1)
    assert dr is None
    assert any("status" in e.field for e in errors)


def test_validate_empty_deciders_ok_when_not_required():
    file = _make_file()
    raw = RawDecisionRecord(
        _file=file, _id=1, title="T", status="accepted",
        date=datetime.date(2024, 1, 1), deciders=[],
    )
    dr, errors = raw.validate(validate_id_len=False, padded_id_len=3, required_deciders_count=0)
    assert errors == []
    assert dr.deciders == []


def test_invalid_metadata_error_message_format():
    from mkdocs_decision_records._model_record import InvalidMetaDataError

    page = MagicMock(spec=["file"])
    page.file = MagicMock(spec=["src_path"])
    page.file.src_path = "adr/001.md"
    err = InvalidMetaDataError(page, "id", "Required")
    assert "id" in err.field
    assert "adr/001.md" in err.message
    assert "Required" in str(err)
