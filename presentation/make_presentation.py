# -*- coding: utf-8 -*-
"""Генерує презентацію до ЛР2: python presentation/make_presentation.py"""
import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "https://github.com/dissimilatee/Lab2XO"

BG = RGBColor(0x0F, 0x17, 0x2A)
PANEL = RGBColor(0x1B, 0x27, 0x42)
ACCENT = RGBColor(0x2D, 0xD4, 0xBF)
TEXT = RGBColor(0xF1, 0xF5, 0xF9)
MUTED = RGBColor(0x94, 0xA3, 0xB8)
FONT = "Calibri"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


def slide():
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG
    return s


def text(s, x, y, w, h, t, size=20, color=TEXT, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, font=FONT):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    lines = t if isinstance(t, list) else [t]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run()
        r.text = line
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = color
        r.font.name = font
        if i:
            p.space_before = Pt(size * 0.45)
    return tb


def title(s, t, sub=None):
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.7), Inches(0.62), Inches(0.12), Inches(0.62))
    bar.fill.solid(); bar.fill.fore_color.rgb = ACCENT; bar.line.fill.background()
    text(s, 1.0, 0.5, 11.5, 0.9, t, 34, TEXT, True, anchor=MSO_ANCHOR.MIDDLE)
    if sub:
        text(s, 1.0, 1.3, 11.5, 0.5, sub, 16, MUTED)


def box(s, x, y, w, h, fill=PANEL, line=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    b = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    b.fill.solid(); b.fill.fore_color.rgb = fill
    if line:
        b.line.color.rgb = line; b.line.width = Pt(1.5)
    else:
        b.line.fill.background()
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        b.adjustments[0] = 0.08
    b.shadow.inherit = False
    return b


def card(s, x, y, w, h, head, body, size=22):
    box(s, x, y, w, h)
    text(s, x + 0.3, y + 0.2, w - 0.6, 0.5, head, 20, ACCENT, True)
    text(s, x + 0.3, y + 0.8, w - 0.6, h - 1.0, body, size, TEXT)


def arrow(s, x, y, w=0.7):
    a = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x), Inches(y), Inches(w), Inches(0.45))
    a.fill.solid(); a.fill.fore_color.rgb = ACCENT; a.line.fill.background()


def footer(s, n):
    text(s, 0.7, 7.0, 8, 0.35, "Хмарні обчислення · ЛР2 · Сканер чеків", 11, MUTED)
    text(s, 11.9, 7.0, 0.8, 0.35, str(n), 11, MUTED, align=PP_ALIGN.RIGHT)


def notes(s, t):
    s.notes_slide.notes_text_frame.text = t


# 1. Титул
s = slide()
band = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.35), prs.slide_height)
band.fill.solid(); band.fill.fore_color.rgb = ACCENT; band.line.fill.background()
text(s, 1.0, 1.6, 11, 0.5, "Лабораторна робота № 2 · Хмарні обчислення", 20, ACCENT, True)
text(s, 1.0, 2.2, 11.5, 1.6, "Сканер чеків із фото", 54, TEXT, True)
text(s, 1.0, 3.5, 11.5, 1.0, "Інтеграція зовнішнього API: Google Gemini API + Streamlit", 26, MUTED)
text(s, 1.0, 5.4, 11, 1.0, ["Виконав: Бондаренко Максим, ТТП-42",
                            "Київський національний університет імені Тараса Шевченка, 2026"], 18, TEXT)
notes(s, "Привітання, назва проєкту: застосунок, який перетворює фото чека на таблицю.")

# 2. Суть проєкту
s = slide(); title(s, "Суть проєкту", "Фото чека → структуровані дані за кілька секунд")
card(s, 0.7, 1.9, 5.9, 4.6, "Проблема", [
    "• Чеки паперові, вицвілі, у різних форматах",
    "• Облік витрат вручну: довго й з помилками",
    "• Класичний OCR дає «сирий» текст, а не таблицю",
])
card(s, 6.9, 1.9, 5.7, 4.6, "Рішення", [
    "• Користувач завантажує фото чека",
    "• Мультимодальна модель Gemini читає його й повертає JSON за заданою схемою",
    "• Застосунок показує таблицю, перевіряє суму й віддає CSV",
])
footer(s, 2)
notes(s, "Проблема: ручне введення витрат. Рішення: одне фото, Gemini повертає структурований JSON.")

# 3. Сценарії використання
s = slide(); title(s, "Сценарії використання")
items = [
    ("Особисті фінанси", "Облік витрат: чек → CSV → таблиця витрат за категоріями"),
    ("Бухгалтерія малого бізнесу", "Швидке внесення авансових звітів і чеків від працівників"),
    ("Відрядження та звіти", "Розпізнавання пачки чеків замість ручного переписування"),
    ("Гарантія й повернення", "Зберегти дату, магазин і суму покупки у структурованому вигляді"),
]
for i, (h, b) in enumerate(items):
    x = 0.7 + (i % 2) * 6.1
    y = 1.7 + (i // 2) * 2.5
    card(s, x, y, 5.9, 2.25, h, b, 19)
footer(s, 3)
notes(s, "Чотири типові сценарії. Основний для демо: особисті фінанси.")

# 4. Використані API
s = slide(); title(s, "Використані API та сервіси")
rows = [
    ("Сервіс", "Призначення", "Як підключено"),
    ("Google Gemini API", "Розпізнавання зображення та видача JSON", "google-genai SDK, HTTPS, ключ GEMINI_API_KEY"),
    ("Structured output", "Відповідь суворо за схемою Receipt", "response_schema + pydantic"),
    ("Streamlit", "Веб-інтерфейс: завантаження, таблиця, CSV", "Python, запуск streamlit run app.py"),
    ("GitHub", "Код і документація проєкту", "Репозиторій Lab2XO, ключ API не зберігається"),
]
tbl = s.shapes.add_table(len(rows), 3, Inches(0.7), Inches(1.7), Inches(11.9), Inches(4.2)).table
for c, w in enumerate([3.3, 4.6, 4.0]):
    tbl.columns[c].width = Inches(w)
for r, row in enumerate(rows):
    for c, val in enumerate(row):
        cell = tbl.cell(r, c)
        cell.text = val
        cell.fill.solid()
        cell.fill.fore_color.rgb = ACCENT if r == 0 else (PANEL if r % 2 else BG)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        for p in cell.text_frame.paragraphs:
            for run in p.runs:
                run.font.size = Pt(17); run.font.name = FONT; run.font.bold = (r == 0 or c == 0)
                run.font.color.rgb = BG if r == 0 else TEXT
footer(s, 4)
notes(s, "Головний зовнішній сервіс: Gemini API. Структурований вивід дозволяє не парсити текст.")

# 5. Взаємодія сервісів
s = slide(); title(s, "Взаємодія сервісів", "Шлях одного запиту")
nodes = [("Користувач", "браузер"), ("Streamlit", "app.py"), ("receipt_api.py", "промпт + схема"), ("Gemini API", "google-genai, HTTPS")]
x0, w, gap = 0.7, 2.55, 0.55
for i, (h, b) in enumerate(nodes):
    x = x0 + i * (w + gap)
    box(s, x, 2.3, w, 1.7, PANEL, ACCENT)
    text(s, x, 2.55, w, 0.6, h, 22, TEXT, True, PP_ALIGN.CENTER)
    text(s, x, 3.2, w, 0.6, b, 15, MUTED, False, PP_ALIGN.CENTER)
    if i < 3:
        arrow(s, x + w + 0.03, 2.95, gap - 0.06)
steps = [
    "1. Користувач завантажує фото й натискає «Розпізнати».",
    "2. Streamlit передає байти зображення в receipt_api.extract_receipt().",
    "3. Запит: зображення + промпт українською + схема Receipt (pydantic) → Gemini API.",
    "4. Gemini повертає JSON за схемою; SDK парсить його в об’єкт Receipt.",
    "5. Застосунок будує таблицю, перевіряє суму позицій із підсумком чека й пропонує CSV.",
]
text(s, 0.9, 4.45, 11.6, 2.4, steps, 19, TEXT)
footer(s, 5)
notes(s, "Пройти по ланцюжку зліва направо: браузер → Streamlit → модуль API → Gemini та назад.")

# 6. Код
s = slide(); title(s, "Ключовий фрагмент коду", "receipt_api.py: запит до Gemini зі схемою відповіді")
box(s, 0.7, 1.9, 11.9, 4.7, RGBColor(0x0B, 0x11, 0x20), None)
code = [
    "class Receipt(BaseModel):",
    "    store_name: Optional[str]; date: Optional[str]; currency: Optional[str]",
    "    items: List[Item]; total: Optional[float]",
    "",
    "response = client.models.generate_content(",
    "    model=\"gemini-3.8-flash\",",
    "    contents=[types.Part.from_bytes(data=image_bytes, mime_type=mime), PROMPT],",
    "    config=types.GenerateContentConfig(",
    "        response_mime_type=\"application/json\",",
    "        response_schema=Receipt, temperature=0))",
    "receipt = response.parsed      # готовий об’єкт, без ручного парсингу",
]
text(s, 1.0, 2.1, 11.4, 4.3, code, 16, RGBColor(0xA7, 0xF3, 0xD0), font="Menlo")
footer(s, 6)
notes(s, "Схема відповіді описана pydantic-класами; temperature=0 для відтворюваності.")

# 7. Демо
s = slide(); title(s, "Демо: вхід і результат")
s.shapes.add_picture(os.path.join(ROOT, "samples", "sample_receipt.png"), Inches(0.7), Inches(1.7), height=Inches(4.7))
text(s, 0.7, 6.45, 4.5, 0.4, "Вхід: фото чека (тестові дані)", 14, MUTED)
s.shapes.add_picture(os.path.join(ROOT, "docs", "demo_table.jpg"), Inches(6.2), Inches(1.7), width=Inches(6.4))
text(s, 6.2, 6.05, 6.4, 0.4, "Результат у застосунку: таблиця, перевірка суми, CSV", 14, MUTED)
footer(s, 7)
notes(s, "Тут показати живе демо: «Взяти приклад чека» → «Розпізнати». Запит може тривати до 1,5 хвилини.")

# 8. Результати
s = slide(); title(s, "Результати та обмеження")
card(s, 0.7, 1.7, 5.9, 4.9, "Що вийшло", [
    "• Усі 5 позицій, магазин, дату й суму розпізнано правильно",
    "• Сума позицій = 399,20 = сума чека",
    "• 4 автоматичні тести без мережі проходять",
    "• Експорт у CSV для Excel",
])
card(s, 6.9, 1.7, 5.7, 4.9, "Обмеження", [
    "• Час відповіді моделі: 72–94 с на один чек",
    "• ≈2000 токенів на запит",
    "• Якість залежить від фото (різкість, освітлення)",
    "• Потрібен інтернет і ключ API",
])
footer(s, 8)
notes(s, "Чесно назвати затримку: це час відповіді API, а не застосунку.")

# 9. Відео
s = slide(); title(s, "Відео демонстрації")
box(s, 0.7, 1.8, 11.9, 4.6, PANEL, ACCENT)
text(s, 0.7, 2.6, 11.9, 1.0, "Запис екрана: завантаження чека → «Розпізнати» → таблиця → CSV", 24, TEXT, True,
     PP_ALIGN.CENTER)
text(s, 0.7, 3.8, 11.9, 1.2, "Відео: [вставити посилання або файл]", 22, ACCENT, False, PP_ALIGN.CENTER)
footer(s, 9)
notes(s, "Вставити відео (Insert → Video) або посилання перед захистом.")

# 10. GitHub
s = slide(); title(s, "Код і запуск")
box(s, 0.7, 1.8, 11.9, 1.4, PANEL, ACCENT)
text(s, 0.7, 2.0, 11.9, 1.0, REPO, 30, ACCENT, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
text(s, 0.9, 3.7, 11.5, 3.0, [
    "Запуск локально:",
    "pip install -r requirements.txt",
    "cp .env.example .env   # вписати GEMINI_API_KEY",
    "streamlit run app.py",
], 20, TEXT, font="Menlo")
text(s, 0.9, 6.3, 11.5, 0.5, "Дякую за увагу!", 22, ACCENT, True)
footer(s, 10)

out = os.path.join(ROOT, "Презентація_ЛР2_Бондаренко.pptx")
prs.core_properties.author = "Бондаренко Максим"
prs.core_properties.title = "Сканер чеків із фото (ЛР2)"
prs.save(out)
print(out)
