# ЛР2: Сканер чеків (Streamlit + Google Gemini API)

PoC-застосунок: користувач завантажує фото касового чека, Gemini API витягує з нього магазин, дату,
позиції та загальну суму у вигляді JSON за схемою (structured output). Застосунок показує таблицю,
звіряє суму позицій із сумою чека й дозволяє завантажити CSV.

## Як це працює
`app.py` (Streamlit UI) -> `receipt_api.py` (google-genai SDK, `models.generate_content`) -> Gemini API (HTTPS, API key).
Відповідь парситься в pydantic-модель `Receipt` (`response_schema`), `check_total` перевіряє суму.

## Запуск
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env        # вписати свій ключ з https://aistudio.google.com/apikey
    streamlit run app.py
Приклад чека: `samples/sample_receipt.png` (вигадані дані; створюється `make_sample_receipt.py`).

## Тести (без мережі)
    python3 tests/test_receipt.py

## Хмара
Ключ задається у `.env` локально або у Streamlit Secrets (`GEMINI_API_KEY`) при деплої на Streamlit Community Cloud.
Модель змінюється змінною `GEMINI_MODEL` (за замовчуванням `gemini-3.1-flash-lite`).
Якщо модель перевантажена (503/504) або недоступна, застосунок пробує запасні (`FALLBACK_MODELS` у `receipt_api.py`); таймаут запиту 60 с.
