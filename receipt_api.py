"""Розпізнавання чеків через Google Gemini API (google-genai SDK).

Фото чека відправляється в модель разом із підказкою; відповідь повертається
у вигляді JSON за схемою Receipt (structured output), тому парсити текст не потрібно.
"""
import os
from typing import List, Optional

from pydantic import BaseModel, Field

DEFAULT_MODEL = "gemini-3.1-flash-lite"
# Якщо модель перевантажена (503/504) або недоступна, пробуємо запасні.
FALLBACK_MODELS = ["gemini-3.8-flash", "gemini-3.5-flash"]
TIMEOUT_MS = 60000

PROMPT = (
    "Це фото касового чека. Витягни з нього дані: назву магазину, дату (формат YYYY-MM-DD, "
    "якщо видно), валюту, перелік позицій (назва, кількість, ціна за одиницю, сума по позиції) "
    "та загальну суму до сплати. Якщо поле не видно, лиши його порожнім. "
    "Числа повертай як числа, без валюти й пробілів."
)


class Item(BaseModel):
    name: str = Field(description="Назва товару")
    quantity: float = Field(default=1, description="Кількість")
    price: float = Field(default=0, description="Ціна за одиницю")
    total: float = Field(default=0, description="Сума по позиції")


class Receipt(BaseModel):
    store_name: Optional[str] = Field(default=None, description="Назва магазину")
    date: Optional[str] = Field(default=None, description="Дата у форматі YYYY-MM-DD")
    currency: Optional[str] = Field(default=None, description="Валюта, наприклад UAH")
    items: List[Item] = Field(default_factory=list)
    total: Optional[float] = Field(default=None, description="Загальна сума чека")


def make_client(api_key: Optional[str] = None):
    """Створює клієнт Gemini. Ключ береться з аргументу або зі змінної GEMINI_API_KEY."""
    from google import genai

    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("Не задано GEMINI_API_KEY (див. .env.example)")
    from google.genai import types

    return genai.Client(api_key=key, http_options=types.HttpOptions(timeout=TIMEOUT_MS))


def extract_receipt(image_bytes: bytes, mime_type: str, client=None, model: Optional[str] = None):
    """Відправляє фото в Gemini і повертає (Receipt, кількість токенів)."""
    from google.genai import types

    client = client or make_client()
    first = model or os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    models = [first] + [m for m in FALLBACK_MODELS if m != first]
    contents = [types.Part.from_bytes(data=image_bytes, mime_type=mime_type), PROMPT]
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=Receipt,
        temperature=0,
    )
    last_error = None
    for name in models:
        try:
            response = client.models.generate_content(model=name, contents=contents, config=config)
            break
        except Exception as e:  # перевантаження, таймаут, модель знята
            last_error = e
    else:
        raise last_error
    receipt = response.parsed
    if receipt is None:
        receipt = Receipt.model_validate_json(response.text)
    usage = getattr(response, "usage_metadata", None)
    tokens = getattr(usage, "total_token_count", None) if usage else None
    return receipt, tokens


def items_table(receipt: Receipt):
    """Позиції чека у вигляді pandas.DataFrame."""
    import pandas as pd

    return pd.DataFrame(
        [{"Назва": i.name, "К-сть": i.quantity, "Ціна": i.price, "Сума": i.total} for i in receipt.items]
    )


def check_total(receipt: Receipt, tolerance: float = 0.05):
    """Звіряє суму позицій із загальною сумою чека. Повертає (ok, сума_позицій)."""
    s = round(sum(i.total for i in receipt.items), 2)
    if receipt.total is None:
        return True, s
    return abs(s - receipt.total) <= tolerance, s
