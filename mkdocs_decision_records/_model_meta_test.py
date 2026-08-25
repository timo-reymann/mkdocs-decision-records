from mkdocs_decision_records._model_meta import MetaModel


def test_add_and_get():
    model = MetaModel()
    model.add("Status", "accepted")
    assert model.get("Status") == "accepted"


def test_get_missing_key_returns_none():
    model = MetaModel()
    assert model.get("Missing") is None


def test_get_all_preserves_order():
    model = MetaModel()
    model.add("a", 1)
    model.add("b", 2)
    model.add("a", 3)
    assert model.get_all() == [("a", 1), ("b", 2), ("a", 3)]


def test_get_returns_first_match():
    model = MetaModel()
    model.add("key", "first")
    model.add("key", "second")
    assert model.get("key") == "first"


def test_empty_model():
    model = MetaModel()
    assert model.get_all() == []
    assert model.get("anything") is None


def test_add_various_value_types():
    model = MetaModel()
    model.add("str", "hello")
    model.add("int", 42)
    model.add("list", [1, 2, 3])
    assert model.get("str") == "hello"
    assert model.get("int") == 42
    assert model.get("list") == [1, 2, 3]
