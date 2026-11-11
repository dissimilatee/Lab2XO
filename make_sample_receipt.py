"""Створює навчальний приклад чека (вигадані дані) для демонстрації."""
from PIL import Image, ImageDraw, ImageFont

FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
lines = [
    ("ТЕСТОВИЙ МАГАЗИН «ГАСТРОНОМ»", True), ("м. Київ, вул. Прикладна, 1", False), ("", False),
    ("Чек № 000123      01.11.2026  14:32", False), ("-" * 38, False),
    ("Хліб житній           2 x 25.00      50.00", False),
    ("Молоко 2.5%           1 x 40.50      40.50", False),
    ("Сир твердий 0.350кг   1 x 189.90    189.90", False),
    ("Яблука 1.2кг          1 x 64.80      64.80", False),
    ("Вода мінеральна       3 x 18.00      54.00", False), ("-" * 38, False),
    ("РАЗОМ, UAH:                         399.20", True), ("Картка                               399.20", False),
    ("", False), ("ДЯКУЄМО ЗА ПОКУПКУ!", True),
]
f, fb = ImageFont.truetype(FONT, 22), ImageFont.truetype(BOLD, 22)
img = Image.new("RGB", (640, 60 + 34 * len(lines)), "#fbfbf6")
d = ImageDraw.Draw(img)
for i, (t, b) in enumerate(lines):
    d.text((30, 30 + 34 * i), t, fill="#222", font=fb if b else f)
img.save("samples/sample_receipt.png")
print("saved")
