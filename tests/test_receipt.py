"""Тести без мережі: підміна клієнта Gemini."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from receipt_api import Receipt, Item, check_total, extract_receipt, items_table  # noqa: E402

SAMPLE = {
    "store_name": "Тестовий магазин", "date": "2026-11-01", "currency": "UAH",
    "items": [{"name": "Хліб", "quantity": 2, "price": 25.0, "total": 50.0},
              {"name": "Молоко", "quantity": 1, "price": 40.5, "total": 40.5}],
    "total": 90.5,
}


class FakeResponse:
    def __init__(self, parsed=None, text=None):
        self.parsed = parsed
        self.text = text
        self.usage_metadata = type("U", (), {"total_token_count": 123})()


class FakeModels:
    def __init__(self, resp): self.resp = resp; self.kwargs = None
    def generate_content(self, **kw): self.kwargs = kw; return self.resp


class FakeClient:
    def __init__(self, resp): self.models = FakeModels(resp)


def test_parsed_response():
    c = FakeClient(FakeResponse(parsed=Receipt(**SAMPLE)))
    r, tokens = extract_receipt(b"img", "image/jpeg", client=c, model="m")
    assert r.store_name == "Тестовий магазин" and tokens == 123
    assert c.models.kwargs["model"] == "m"


def test_json_text_fallback():
    c = FakeClient(FakeResponse(parsed=None, text=json.dumps(SAMPLE)))
    r, _ = extract_receipt(b"img", "image/png", client=c)
    assert len(r.items) == 2 and r.total == 90.5


def test_table_and_total_check():
    r = Receipt(**SAMPLE)
    assert list(items_table(r).columns) == ["Назва", "К-сть", "Ціна", "Сума"]
    assert check_total(r) == (True, 90.5)
    r.total = 100
    assert check_total(r)[0] is False


def test_missing_fields_ok():
    r = Receipt(items=[Item(name="X")])
    assert r.total is None and check_total(r)[0] is True


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("ok", name)
