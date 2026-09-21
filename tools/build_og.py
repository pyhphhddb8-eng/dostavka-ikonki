"""Картинки превью 1200×630 — по одной на страницу, из одного шаблона.

Текст берётся из content/pages.tsv. Добавили строку — получили картинку,
и ничего не нужно рисовать руками.
"""

from PIL import Image, ImageDraw, ImageFont

from tools import build_font, mark, pages

CARD = (1200, 630)
MAX_BYTES = 300 * 1024

MARGIN = 84
TEXT_WIDTH = CARD[0] - MARGIN * 2
MUTED = "#93A9D4"

# Полоса, внутри которой по центру встаёт подпись, и высота строки.
CAPTION_BAND = (214, 528)
LINE_HEIGHT = 98

_FONTS = {}


def font(weight, size):
    key = (weight, size)
    if key not in _FONTS:
        src = build_font.BOLD if weight >= 700 else build_font.REGULAR
        if not src.exists():
            build_font.main()
        _FONTS[key] = ImageFont.truetype(str(src), size)
    return _FONTS[key]


_MEASURE = ImageDraw.Draw(Image.new("RGB", (1, 1)))


def wrap(text, weight, size, max_width):
    """Разложить строку по строкам, не шире max_width."""
    face = font(weight, size)
    lines = []
    current = ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if not current or _MEASURE.textlength(trial, font=face) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def render(page):
    img = Image.new("RGB", CARD, mark.FIELD)
    d = ImageDraw.Draw(img)

    # Жёлтая полоса у левого края — по ней карточка узнаётся в ленте чата.
    d.rectangle([0, 0, 17, CARD[1]], fill=mark.ARROW)

    # Знак и название сайта.
    badge = mark.png(96, background=mark.FIELD).convert("RGB")
    img.paste(badge, (MARGIN, 66))
    d.text((MARGIN + 124, 74), pages.SITE_NAME, font=font(700, 48), fill=mark.ARROW)
    d.text((MARGIN + 126, 134), "доставка по городу", font=font(400, 26), fill=MUTED)

    # Подпись — главное, что видно в карточке. Блок ставится по центру
    # свободного поля, иначе короткая подпись в одну строку виснет вверху,
    # а под ней остаётся пустота во весь экран.
    lines = wrap(page.caption, 700, 86, TEXT_WIDTH)[:3]
    top, bottom = CAPTION_BAND
    y = top + ((bottom - top) - len(lines) * LINE_HEIGHT) // 2

    # Короткий жёлтый штрих над подписью — тот же акцент, что и полоса слева.
    d.rectangle([MARGIN, y - 34, MARGIN + 104, y - 26], fill=mark.ARROW)

    for line in lines:
        d.text((MARGIN, y), line, font=font(700, 86), fill="#FFFFFF")
        y += LINE_HEIGHT

    d.text(
        (MARGIN, CARD[1] - 74),
        "Демонстрационная работа · компания вымышленная",
        font=font(400, 26),
        fill=MUTED,
    )
    return img


def main():
    out = pages.ROOT / "icons" / "og"
    out.mkdir(parents=True, exist_ok=True)
    for page in pages.load():
        path = pages.ROOT / page.og_image_rel
        render(page).save(path, optimize=True)
        size = path.stat().st_size
        if size >= MAX_BYTES:
            raise SystemExit(
                "%s весит %d КБ — WhatsApp такую в карточке пропустит"
                % (path.name, size // 1024)
            )


if __name__ == "__main__":
    main()
