"""Знак «Прямиком»: скруглённый квадрат и широкая стрелка вправо-вверх.

Геометрия описана здесь один раз. И SVG, и все растровые размеры берутся
отсюда, поэтому вектор и растр не могут разойтись.

Две фигуры, без текста и мелких деталей: настоящий размер значка во вкладке —
16 пикселей, и всё, что тоньше линии в этом размере, превращается в грязь.
"""

import math

from PIL import Image, ImageDraw

FIELD = "#0A2A66"        # глубокий синий — поле знака
ARROW = "#FFC61A"        # жёлтый — стрелка
RADIUS_RATIO = 0.22      # радиус скругления как доля стороны

# Стрелка описана в квадрате 100×100 направленной вправо, одним контуром:
# ножка, затем плечо головы, остриё, второе плечо, обратно к ножке.
_ARROW_RIGHT = [
    (18.0, 39.0),
    (50.0, 39.0),
    (50.0, 20.0),
    (86.0, 50.0),
    (50.0, 80.0),
    (50.0, 61.0),
    (18.0, 61.0),
]

_ANGLE_DEG = -45.0   # в экранных координатах (ось Y вниз) это поворот вверх
_SCALE = 1.15        # насколько стрелка заполняет поле после поворота

# Сглаживание: рисуем крупно и уменьшаем. Иначе на 16 пикселях края рвутся.
_SUPERSAMPLE = 8


def _rotated_scaled():
    """Точки стрелки в квадрате 100×100: повёрнуты, отмасштабированы,
    и заново поставлены по центру поля."""
    a = math.radians(_ANGLE_DEG)
    ca, sa = math.cos(a), math.sin(a)
    pts = []
    for x, y in _ARROW_RIGHT:
        dx, dy = x - 50.0, y - 50.0
        pts.append((dx * ca - dy * sa, dx * sa + dy * ca))

    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    cx = (min(xs) + max(xs)) / 2.0
    cy = (min(ys) + max(ys)) / 2.0
    return [((x - cx) * _SCALE + 50.0, (y - cy) * _SCALE + 50.0) for x, y in pts]


_ARROW_100 = _rotated_scaled()


def arrow_points(size):
    """Контур стрелки для квадрата со стороной `size`."""
    k = size / 100.0
    return [(x * k, y * k) for x, y in _ARROW_100]


def svg(size=512):
    """Текст SVG-файла со знаком."""
    r = RADIUS_RATIO * size
    pts = " ".join("%.2f,%.2f" % (x, y) for x, y in arrow_points(size))
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'width="%d" height="%d" viewBox="0 0 %d %d" '
        'role="img" aria-label="Прямиком">'
        '<rect width="%d" height="%d" rx="%.2f" ry="%.2f" fill="%s"/>'
        '<polygon points="%s" fill="%s"/>'
        '</svg>'
    ) % (size, size, size, size, size, size, r, r, FIELD, pts, ARROW)


def png(size, background=None):
    """Картинка знака со стороной `size`.

    `background` — цвет подложки. Нужен для apple-touch-icon: iOS не умеет
    прозрачность и подставляет вместо неё чёрный.
    """
    big = size * _SUPERSAMPLE
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(
        [0, 0, big - 1, big - 1],
        radius=RADIUS_RATIO * big,
        fill=FIELD,
    )
    d.polygon(arrow_points(big), fill=ARROW)
    img = img.resize((size, size), Image.LANCZOS)

    if background is not None:
        plate = Image.new("RGBA", (size, size), background)
        plate.alpha_composite(img)
        img = plate
    return img


def _channel(value):
    c = value / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_colour):
    """Относительная яркость цвета по WCAG."""
    h = hex_colour.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast(hex_a, hex_b):
    """Отношение контраста пары цветов. Считается по формуле, а не на глаз."""
    la, lb = luminance(hex_a), luminance(hex_b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)
