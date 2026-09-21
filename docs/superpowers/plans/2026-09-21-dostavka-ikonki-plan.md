# Значок сайта и превью ссылок для службы доставки — план работ

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Собрать демо-сайт вымышленной службы доставки «Прямиком» из трёх страниц с полным комплектом значков, отдельным превью 1200×630 у каждой страницы, витриной из живых тегов и скриптом проверок, и выложить на GitHub Pages.

**Architecture:** Статические HTML-страницы в корне репозитория, без npm и без единой зависимости в браузере. Вся сборка — скрипты на Python в `tools/`: геометрия знака описана один раз и выдаёт и SVG, и все растровые размеры; тексты трёх страниц лежат одной строкой на страницу в `content/pages.tsv`, из них же собираются картинки превью и подставляются мета-теги в размеченный участок шапки каждой страницы. Витрина ничего не знает о текстах заранее: она запрашивает живые страницы того же сайта, разбирает их шапку и строит карточки из найденного.

**Tech Stack:** Python 3.9 (системный), Pillow 11.3 и fontTools 4.60 (только на этапе сборки, в браузер не попадают), стандартный `unittest` для тестов, PT Sans под лицензией OFL, GitHub Pages для выкладки.

**Spec:** `docs/superpowers/specs/2026-09-21-dostavka-ikonki-design.md`

## Глобальные ограничения

Эти требования действуют во всех задачах без исключения.

- Ни одной зависимости в браузере: ни CDN, ни шрифта извне, ни аналитики. Страница не делает ни одного запроса за пределы своего адреса.
- Никакого npm, никакого `package.json`. Сборка — только Python.
- Pillow и fontTools уже установлены в системный Python 3.9. Ничего доустанавливать не нужно и нельзя.
- Онлайновые генераторы фавиконов не используются. Все файлы значка рождаются из `tools/mark.py`.
- На сайте нет ни одной формы, ни одного поля, отправляющего данные. Поле ввода номера заказа на `track.html` обрабатывается на самой странице и никуда ничего не шлёт.
- Компания вымышленная. На каждой странице видимая глазом пометка об этом.
- Закрытие от поисковиков — только мета-тегом `<meta name="robots" content="noindex, nofollow">`. В `robots.txt` глухого `Disallow: /` быть не должно: боты мессенджеров его читают, и карточка не соберётся.
- Базовый адрес: `https://pyhphhddb8-eng.github.io/dostavka-ikonki/`. Он задан один раз в `tools/pages.py` как `BASE_URL` и больше нигде руками не пишется.
- Название сайта: `Прямиком`. Задано один раз как `SITE_NAME` в `tools/pages.py`.
- Цвета знака: поле `#0A2A66`, стрелка `#FFC61A`. Заданы один раз в `tools/mark.py`.
- Адреса картинок превью (`og:image`, `twitter:image`) — абсолютные, начинаются с `https://`. Остальные адреса в шапке — относительные.
- Каждый коммит заканчивается строкой:
  `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`
- Текст на страницах и в документации — по-русски, обычными словами.

---

## Состав файлов

Сайт лежит в корне репозитория, потому что GitHub Pages будет раздавать ветку `main` из корня — так не нужен ни отдельный workflow, ни папка `/docs` под сайт.

```
dostavka-ikonki/
├── index.html               главная
├── track.html               «Отследить заказ»
├── promo.html               страница акции
├── showcase.html            витрина: карточки из живых тегов + контактный лист значка
├── styles.css               единственный файл стилей на все страницы
├── site.webmanifest         ради значка на домашнем экране Android, и только
├── robots.txt               без глухого Disallow
├── .nojekyll                чтобы Pages не пропускал файлы через Jekyll
├── fonts/
│   ├── ptsans-400.woff2     подрезанный PT Sans, обычный
│   ├── ptsans-700.woff2     подрезанный PT Sans, жирный
│   └── OFL.txt              лицензия шрифта
├── icons/
│   ├── favicon.svg          знак векторный
│   ├── favicon.ico          три кадра: 16, 32, 48
│   ├── icon-16.png … icon-512.png
│   ├── apple-touch-icon.png 180×180, без прозрачности
│   └── og/
│       ├── index.png        1200×630
│       ├── track.png
│       └── promo.png
├── content/
│   └── pages.tsv            один источник текстов: строка на страницу
├── tools/
│   ├── mark.py              геометрия и цвета знака; выдаёт SVG и растр
│   ├── pages.py             чтение content/pages.tsv, адреса, SITE_NAME, BASE_URL
│   ├── build_icons.py       все файлы в icons/
│   ├── build_og.py          три картинки в icons/og/
│   ├── build_font.py        скачивание и подрезка PT Sans
│   ├── build_heads.py       подстановка тегов в шапки страниц
│   ├── build.py             всё сразу, в правильном порядке
│   ├── check.py             проверки: и по файлам, и по живому адресу
│   └── fonts_src/           полные TTF PT Sans, исходник для подрезки
├── tests/
│   ├── test_mark.py
│   ├── test_pages.py
│   ├── test_icons.py
│   ├── test_og.py
│   ├── test_heads.py
│   └── test_check.py
└── docs/
    ├── superpowers/specs/2026-09-21-dostavka-ikonki-design.md
    ├── superpowers/plans/2026-09-21-dostavka-ikonki-plan.md
    └── УСТАНОВКА.md         инструкция владельцу чужого сайта
```

Почему так поделено: `mark.py` держит геометрию и ничего не пишет на диск, `build_*.py` пишут на диск и ничего не вычисляют. Поэтому геометрию можно проверить тестом, не создавая файлов, а сборщики остаются в десяток строк каждый.

Тесты запускаются одной командой из корня:

```bash
python3 -m unittest discover -s tests -v
```

---

## Задача 1: Знак — геометрия, цвета, контраст

**Файлы:**
- Создать: `tools/mark.py`
- Создать: `tests/test_mark.py`
- Создать: `tools/__init__.py` (пустой, чтобы `from tools import mark` работал из корня)

**Интерфейсы:**
- Потребляет: ничего.
- Отдаёт наружу:
  - `mark.FIELD = "#0A2A66"`, `mark.ARROW = "#FFC61A"`, `mark.RADIUS_RATIO = 0.22`
  - `mark.arrow_points(size: float) -> list[tuple[float, float]]` — семь точек контура стрелки, уже повёрнутых и отмасштабированных под квадрат `size × size`
  - `mark.svg(size: int = 512) -> str` — готовый текст SVG-файла
  - `mark.png(size: int) -> PIL.Image.Image` — картинка RGBA `size × size`
  - `mark.contrast(hex_a: str, hex_b: str) -> float` — отношение контраста по формуле WCAG

- [ ] **Шаг 1: Написать падающий тест**

Создать `tests/test_mark.py`:

```python
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import mark


class TestContrast(unittest.TestCase):
    def test_arrow_reads_on_field(self):
        # Стрелка на поле знака: пара должна проходить порог 4.5:1.
        self.assertGreaterEqual(mark.contrast(mark.FIELD, mark.ARROW), 4.5)

    def test_field_reads_on_light_tab(self):
        # На светлой вкладке знак виден силуэтом синего поля.
        self.assertGreaterEqual(mark.contrast(mark.FIELD, "#FFFFFF"), 3.0)

    def test_arrow_reads_on_dark_tab(self):
        # На тёмной вкладке синее поле почти сливается с фоном,
        # и читаемость держит жёлтая стрелка.
        self.assertGreaterEqual(mark.contrast(mark.ARROW, "#1E1E1E"), 3.0)

    def test_known_value(self):
        self.assertAlmostEqual(mark.contrast("#000000", "#FFFFFF"), 21.0, places=1)


class TestArrowGeometry(unittest.TestCase):
    def test_seven_points(self):
        self.assertEqual(len(mark.arrow_points(100)), 7)

    def test_fits_inside_square(self):
        pts = mark.arrow_points(100)
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        self.assertGreater(min(xs), 10)
        self.assertLess(max(xs), 90)
        self.assertGreater(min(ys), 10)
        self.assertLess(max(ys), 90)

    def test_centred(self):
        pts = mark.arrow_points(100)
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        self.assertAlmostEqual((min(xs) + max(xs)) / 2, 50.0, places=3)
        self.assertAlmostEqual((min(ys) + max(ys)) / 2, 50.0, places=3)

    def test_points_up_and_right(self):
        # Остриё стрелки — самая правая точка, и она выше середины.
        pts = mark.arrow_points(100)
        tip = max(pts, key=lambda p: p[0])
        self.assertLess(tip[1], 50.0)

    def test_scales_linearly(self):
        small = mark.arrow_points(100)
        big = mark.arrow_points(400)
        for (sx, sy), (bx, by) in zip(small, big):
            self.assertAlmostEqual(bx, sx * 4, places=6)
            self.assertAlmostEqual(by, sy * 4, places=6)

    def test_stroke_thick_enough_at_16px(self):
        # Настоящий размер значка во вкладке — 16 пикселей.
        # Толщина ножки стрелки не должна опускаться ниже 3 пикселей,
        # иначе при уменьшении она превратится в грязь.
        pts = mark.arrow_points(16)
        ys = [p[1] for p in pts]
        xs = [p[0] for p in pts]
        diag = ((max(xs) - min(xs)) ** 2 + (max(ys) - min(ys)) ** 2) ** 0.5
        self.assertGreater(diag, 12.0)


class TestRendering(unittest.TestCase):
    def test_svg_has_one_rect_and_one_polygon(self):
        out = mark.svg(512)
        self.assertEqual(out.count("<rect"), 1)
        self.assertEqual(out.count("<polygon"), 1)
        self.assertIn(mark.FIELD, out)
        self.assertIn(mark.ARROW, out)
        self.assertIn('viewBox="0 0 512 512"', out)

    def test_png_size_and_colours(self):
        img = mark.png(64)
        self.assertEqual(img.size, (64, 64))
        self.assertEqual(img.mode, "RGBA")
        # В середине знака — стрелка, значит жёлтый.
        r, g, b, a = img.getpixel((32, 32))
        self.assertEqual(a, 255)
        self.assertGreater(r, 200)
        self.assertGreater(g, 150)
        self.assertLess(b, 100)

    def test_png_corner_is_transparent(self):
        # Углы скруглены, значит самый угол прозрачен.
        img = mark.png(64)
        self.assertLess(img.getpixel((0, 0))[3], 40)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Шаг 2: Запустить тест и убедиться, что он падает**

```bash
cd ~/Progects/dostavka-ikonki && python3 -m unittest discover -s tests -v
```

Ожидается: `ModuleNotFoundError: No module named 'tools'`.

- [ ] **Шаг 3: Написать `tools/mark.py`**

```python
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
_SCALE = 1.25        # насколько стрелка заполняет поле после поворота

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
```

Создать пустой `tools/__init__.py`:

```bash
cd ~/Progects/dostavka-ikonki && touch tools/__init__.py
```

- [ ] **Шаг 4: Запустить тесты и убедиться, что они проходят**

```bash
cd ~/Progects/dostavka-ikonki && python3 -m unittest discover -s tests -v
```

Ожидается: все тесты OK. Если `test_arrow_reads_on_field` падает — цвета трогать нельзя молча, сначала подобрать пару и перепроверить обе крайние вкладки.

- [ ] **Шаг 5: Посмотреть на знак глазами**

```bash
cd ~/Progects/dostavka-ikonki && python3 -c "
from tools import mark
from PIL import Image
sheet = Image.new('RGB', (760, 120), '#FFFFFF')
x = 20
for s in (16, 32, 48, 180):
    sheet.paste(mark.png(s), (x, 60 - s // 2), mark.png(s))
    x += s + 24
sheet.save('/tmp/mark-check.png')
print('/tmp/mark-check.png')
"```

Открыть `/tmp/mark-check.png` и убедиться: на 16 пикселях стрелка всё ещё стрелка, а не пятно. Если нет — увеличить `_SCALE` или толщину ножки в `_ARROW_RIGHT` и перезапустить тесты.

- [ ] **Шаг 6: Коммит**

```bash
cd ~/Progects/dostavka-ikonki && git add tools/mark.py tools/__init__.py tests/test_mark.py && git commit -m "Знак: геометрия, цвета и проверка контраста

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Задача 2: Файлы значка — все размеры, ICO и SVG

**Файлы:**
- Создать: `tools/build_icons.py`
- Создать: `tests/test_icons.py`
- Создаёт на диске: `icons/favicon.svg`, `icons/favicon.ico`, `icons/icon-{16,32,48,180,192,512}.png`, `icons/apple-touch-icon.png`

**Интерфейсы:**
- Потребляет: `mark.svg(size)`, `mark.png(size, background)`, `mark.FIELD` из задачи 1.
- Отдаёт наружу:
  - `build_icons.SIZES = (16, 32, 48, 180, 192, 512)`
  - `build_icons.ICO_SIZES = (16, 32, 48)`
  - `build_icons.main() -> None` — пишет все файлы в `icons/`
  - `build_icons.ROOT` — корень репозитория как `pathlib.Path`

- [ ] **Шаг 1: Написать падающий тест**

Создать `tests/test_icons.py`:

```python
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image

from tools import build_icons, mark

ICONS = build_icons.ROOT / "icons"


class TestIconFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build_icons.main()

    def test_every_declared_size_exists_and_matches_its_name(self):
        for size in build_icons.SIZES:
            path = ICONS / ("icon-%d.png" % size)
            self.assertTrue(path.exists(), "нет файла %s" % path.name)
            with Image.open(path) as img:
                self.assertEqual(
                    img.size, (size, size),
                    "%s внутри %dx%d, а имя обещает %d" % (path.name, img.size[0], img.size[1], size),
                )

    def test_ico_carries_three_frames(self):
        path = ICONS / "favicon.ico"
        self.assertTrue(path.exists())
        with Image.open(path) as img:
            sizes = {s[0] for s in img.ico.sizes()}
        self.assertEqual(sizes, set(build_icons.ICO_SIZES))

    def test_apple_touch_icon_has_no_transparency(self):
        # iOS не умеет прозрачность и подставляет вместо неё чёрный,
        # поэтому под значок кладётся сплошная подложка.
        path = ICONS / "apple-touch-icon.png"
        with Image.open(path) as img:
            self.assertEqual(img.size, (180, 180))
            self.assertEqual(img.mode, "RGB")
            corner = img.getpixel((0, 0))
        expected = tuple(int(mark.FIELD.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
        self.assertEqual(corner, expected)

    def test_svg_is_vector_and_parses(self):
        import xml.etree.ElementTree as ET
        path = ICONS / "favicon.svg"
        tree = ET.parse(path)
        root = tree.getroot()
        self.assertTrue(root.tag.endswith("svg"))

    def test_nothing_is_heavy(self):
        # Значок во вкладке грузится на каждой странице.
        for path in ICONS.glob("icon-*.png"):
            self.assertLess(path.stat().st_size, 40 * 1024, "%s слишком тяжёлый" % path.name)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Шаг 2: Запустить тест и убедиться, что он падает**

```bash
cd ~/Progects/dostavka-ikonki && python3 -m unittest tests.test_icons -v
```

Ожидается: `ImportError: cannot import name 'build_icons'`.

- [ ] **Шаг 3: Написать `tools/build_icons.py`**

```python
"""Раскладка знака по файлам: SVG, ICO и все растровые размеры.

Ни один размер не рисуется руками и не проходит через онлайновый генератор:
все берутся из tools/mark.py.
"""

import pathlib

from tools import mark

ROOT = pathlib.Path(__file__).resolve().parent.parent

SIZES = (16, 32, 48, 180, 192, 512)
ICO_SIZES = (16, 32, 48)


def main():
    out = ROOT / "icons"
    out.mkdir(parents=True, exist_ok=True)

    (out / "favicon.svg").write_text(mark.svg(512), encoding="utf-8")

    for size in SIZES:
        mark.png(size).save(out / ("icon-%d.png" % size), optimize=True)

    # iOS не умеет прозрачность: без подложки углы станут чёрными.
    mark.png(180, background=mark.FIELD).convert("RGB").save(
        out / "apple-touch-icon.png", optimize=True
    )

    # ICO собирается из наших собственных отрисовок каждого размера,
    # а не из одной картинки, ужатой встроенным ресайзом.
    # Порядок важен: Pillow отбрасывает размеры крупнее первого кадра,
    # поэтому первым идёт самый большой.
    largest_first = sorted(ICO_SIZES, reverse=True)
    frames = [mark.png(s).convert("RGBA") for s in largest_first]
    frames[0].save(
        out / "favicon.ico",
        format="ICO",
        sizes=[(s, s) for s in largest_first],
        append_images=frames[1:],
    )


if __name__ == "__main__":
    main()
```

- [ ] **Шаг 4: Запустить тесты и убедиться, что они проходят**

```bash
cd ~/Progects/dostavka-ikonki && python3 -m unittest discover -s tests -v
```

Ожидается: все тесты OK.

Проверено на этой машине: кадр 16 в готовом ICO совпадает с `mark.png(16)`
пиксель в пиксель, то есть Pillow действительно взял наши отрисовки, а не ужал
одну картинку сам.

- [ ] **Шаг 5: Коммит**

```bash
cd ~/Progects/dostavka-ikonki && git add tools/build_icons.py tests/test_icons.py icons && git commit -m "Комплект значка: SVG, ICO и шесть растровых размеров

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Задача 3: Один источник текстов и вшитый шрифт

**Файлы:**
- Создать: `content/pages.tsv`
- Создать: `tools/pages.py`
- Создать: `tools/build_font.py`
- Создать: `tests/test_pages.py`
- Создаёт на диске: `tools/fonts_src/PT_Sans-Web-{Regular,Bold}.ttf`, `fonts/ptsans-{400,700}.woff2`, `fonts/OFL.txt`

**Интерфейсы:**
- Потребляет: ничего из прежних задач.
- Отдаёт наружу:
  - `pages.SITE_NAME = "Прямиком"`
  - `pages.BASE_URL = "https://pyhphhddb8-eng.github.io/dostavka-ikonki/"`
  - `pages.ROOT` — корень репозитория как `pathlib.Path`
  - `pages.Page` с полями `slug`, `title`, `description`, `caption` и свойствами
    `file_name`, `url`, `og_image_rel`, `og_image_url`
  - `pages.load() -> list[Page]` — три страницы в порядке из файла
  - `build_font.main() -> None`
  - `build_font.REGULAR`, `build_font.BOLD` — пути к полным TTF

- [ ] **Шаг 1: Написать падающий тест**

Создать `tests/test_pages.py`:

```python
import itertools
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import pages


class TestSource(unittest.TestCase):
    def setUp(self):
        self.pages = pages.load()

    def test_three_pages(self):
        self.assertEqual([p.slug for p in self.pages], ["index", "track", "promo"])

    def test_nothing_is_empty(self):
        for p in self.pages:
            for field in ("title", "description", "caption"):
                self.assertTrue(getattr(p, field).strip(), "%s: пустое поле %s" % (p.slug, field))

    def test_pages_do_not_repeat_each_other(self):
        # Одна картинка и один текст на весь сайт — самая частая ошибка.
        for field in ("title", "description", "caption", "og_image_url", "url"):
            values = [getattr(p, field) for p in self.pages]
            for a, b in itertools.combinations(values, 2):
                self.assertNotEqual(a, b, "повтор в поле %s: %r" % (field, a))

    def test_site_name_does_not_repeat_the_title(self):
        # Telegram печатает название сайта и заголовок одно под другим.
        for p in self.pages:
            self.assertNotEqual(p.title.strip().lower(), pages.SITE_NAME.strip().lower())

    def test_description_fits_the_card(self):
        # Длинное описание мессенджер обрежет на полуслове.
        for p in self.pages:
            self.assertLessEqual(len(p.description), 160, "%s: описание длиннее 160 знаков" % p.slug)
            self.assertGreaterEqual(len(p.description), 60, "%s: описание короче 60 знаков" % p.slug)

    def test_title_fits_the_card(self):
        for p in self.pages:
            self.assertLessEqual(len(p.title), 70, "%s: заголовок длиннее 70 знаков" % p.slug)

    def test_preview_addresses_are_absolute(self):
        # Относительный адрес картинки — карточка приходит без картинки.
        for p in self.pages:
            self.assertTrue(p.og_image_url.startswith("https://"), p.og_image_url)
            self.assertTrue(p.url.startswith("https://"), p.url)

    def test_index_lives_at_the_root_address(self):
        index = self.pages[0]
        self.assertEqual(index.url, pages.BASE_URL)
        self.assertEqual(index.file_name, "index.html")
        self.assertEqual(self.pages[1].file_name, "track.html")


class TestFont(unittest.TestCase):
    def test_subset_fonts_are_built_and_small(self):
        from tools import build_font
        build_font.main()
        for name in ("ptsans-400.woff2", "ptsans-700.woff2"):
            path = pages.ROOT / "fonts" / name
            self.assertTrue(path.exists(), "нет файла %s" % name)
            self.assertLess(path.stat().st_size, 60 * 1024, "%s слишком тяжёлый" % name)
            with open(path, "rb") as fh:
                self.assertEqual(fh.read(4), b"wOF2", "%s не woff2" % name)

    def test_licence_travels_with_the_font(self):
        self.assertTrue((pages.ROOT / "fonts" / "OFL.txt").exists())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Шаг 2: Запустить тест и убедиться, что он падает**

```bash
cd ~/Progects/dostavka-ikonki && python3 -m unittest tests.test_pages -v
```

Ожидается: `ImportError: cannot import name 'pages'`.

- [ ] **Шаг 3: Написать `content/pages.tsv`**

Поля разделены знаком табуляции. Первая строка — названия колонок. Новая страница сайта — это новая строка здесь, и больше нигде.

```
slug	title	description	caption
index	Доставка посылок и еды по городу за 90 минут	Курьер забирает у двери и привозит по адресу в тот же день: документы, посылки, заказ из кафе.	90 минут по городу
track	Где сейчас мой заказ	Введите номер накладной и посмотрите, на каком этапе посылка и во сколько её ждать сегодня.	Отследить заказ
promo	Первая доставка за 1 рубль	До 30 октября новый клиент платит рубль за первую доставку по городу. Один заказ на один телефон.	Первая доставка за 1 рубль
```

Внимание при вставке: между полями именно табуляция, а не пробелы. Проверить можно так — должно напечатать `4` для каждой строки:

```bash
cd ~/Progects/dostavka-ikonki && awk -F'\t' '{print NF}' content/pages.tsv
```

- [ ] **Шаг 4: Написать `tools/pages.py`**

```python
"""Один источник правды о страницах сайта.

Тексты лежат в content/pages.tsv по строке на страницу. Отсюда же берутся
адреса. Новая страница — новая строка в файле, а не ручная правка четырёх мест.
"""

import csv
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

SITE_NAME = "Прямиком"
BASE_URL = "https://pyhphhddb8-eng.github.io/dostavka-ikonki/"

SOURCE = ROOT / "content" / "pages.tsv"


class Page(object):
    def __init__(self, slug, title, description, caption):
        self.slug = slug
        self.title = title
        self.description = description
        self.caption = caption

    @property
    def file_name(self):
        return "%s.html" % self.slug

    @property
    def url(self):
        """Канонический адрес. Главная живёт на адресе папки, без index.html."""
        if self.slug == "index":
            return BASE_URL
        return BASE_URL + self.file_name

    @property
    def og_image_rel(self):
        return "icons/og/%s.png" % self.slug

    @property
    def og_image_url(self):
        """Адрес картинки превью — всегда абсолютный.
        Мессенджер не подставляет домен сам."""
        return BASE_URL + self.og_image_rel

    def __repr__(self):
        return "<Page %s>" % self.slug


def load(source=None):
    path = pathlib.Path(source) if source else SOURCE
    with open(path, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        return [
            Page(
                row["slug"].strip(),
                row["title"].strip(),
                row["description"].strip(),
                row["caption"].strip(),
            )
            for row in reader
            if row.get("slug", "").strip()
        ]
```

- [ ] **Шаг 5: Написать `tools/build_font.py`**

```python
"""PT Sans: скачать один раз, подрезать, вшить в сайт.

Наружу страницы не ходят, поэтому шрифт лежит своим файлом рядом. Подрезка
оставляет только кириллицу, латиницу, цифры и нужные знаки препинания —
полный PT Sans весит в несколько раз больше без всякой пользы.

Лицензия OFL кладётся рядом со шрифтом: она требует, чтобы копия
распространялась вместе с файлом.
"""

import pathlib
import subprocess
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "tools" / "fonts_src"
OUT_DIR = ROOT / "fonts"

RAW = "https://github.com/google/fonts/raw/main/ofl/ptsans/"

REGULAR = SRC_DIR / "PT_Sans-Web-Regular.ttf"
BOLD = SRC_DIR / "PT_Sans-Web-Bold.ttf"
LICENCE = SRC_DIR / "OFL.txt"

# Латиница и знаки препинания, кириллица, рубль, тире, кавычки-ёлочки.
UNICODES = ",".join([
    "U+0020-007E",
    "U+00A0",
    "U+00AB", "U+00BB",
    "U+2010-2015",
    "U+2018-201F",
    "U+2026",
    "U+2192",
    "U+20BD",
    "U+0400-045F",
    "U+0490-0491",
])


def _download(name, dest):
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    print("скачиваю %s" % name)
    urllib.request.urlretrieve(RAW + name, dest)


def _subset(src, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call([
        sys.executable, "-m", "fontTools.subset", str(src),
        "--unicodes=" + UNICODES,
        "--layout-features=kern,liga",
        "--no-hinting",
        "--desubroutinize",
        "--flavor=woff2",
        "--output-file=" + str(dest),
    ])


def main():
    _download("PT_Sans-Web-Regular.ttf", REGULAR)
    _download("PT_Sans-Web-Bold.ttf", BOLD)
    _download("OFL.txt", LICENCE)

    _subset(REGULAR, OUT_DIR / "ptsans-400.woff2")
    _subset(BOLD, OUT_DIR / "ptsans-700.woff2")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "OFL.txt").write_text(LICENCE.read_text(encoding="utf-8"), encoding="utf-8")


if __name__ == "__main__":
    main()
```

- [ ] **Шаг 6: Запустить тесты и убедиться, что они проходят**

```bash
cd ~/Progects/dostavka-ikonki && python3 -m unittest discover -s tests -v
```

Ожидается: все тесты OK. Первый запуск выйдет в сеть за шрифтом — дальше файлы лежат на диске и сеть не нужна.

- [ ] **Шаг 7: Коммит**

Полные TTF кладутся в репозиторий вместе с лицензией: так сборка повторяется без сети, а требование OFL выполнено.

```bash
cd ~/Progects/dostavka-ikonki && git add content tools/pages.py tools/build_font.py tools/fonts_src fonts tests/test_pages.py && git commit -m "Один источник текстов страниц и вшитый подрезанный PT Sans

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---
## Задача 4: Картинки превью 1200×630 — своя у каждой страницы

**Файлы:**
- Создать: `tools/build_og.py`
- Создать: `tests/test_og.py`
- Создаёт на диске: `icons/og/index.png`, `icons/og/track.png`, `icons/og/promo.png`

**Интерфейсы:**
- Потребляет: `pages.load()`, `pages.SITE_NAME`, `pages.ROOT`, `mark.png()`, `mark.FIELD`, `mark.ARROW`, `build_font.REGULAR`, `build_font.BOLD`.
- Отдаёт наружу:
  - `build_og.CARD = (1200, 630)`
  - `build_og.MAX_BYTES = 300 * 1024`
  - `build_og.render(page) -> PIL.Image.Image`
  - `build_og.main() -> None`

- [ ] **Шаг 1: Написать падающий тест**

Создать `tests/test_og.py`:

```python
import hashlib
import itertools
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image

from tools import build_og, pages


class TestPreviewImages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build_og.main()
        cls.pages = pages.load()

    def _path(self, page):
        return pages.ROOT / page.og_image_rel

    def test_every_page_has_its_own_file(self):
        for p in self.pages:
            self.assertTrue(self._path(p).exists(), "нет картинки для %s" % p.slug)

    def test_exact_card_size(self):
        # Не «примерно два к одному», а ровно 1200×630:
        # иначе мессенджер обрежет картинку по своему усмотрению.
        for p in self.pages:
            with Image.open(self._path(p)) as img:
                self.assertEqual(img.size, (1200, 630), "%s: %s" % (p.slug, img.size))

    def test_light_enough_for_whatsapp(self):
        # Тяжёлую картинку WhatsApp в карточке пропускает.
        for p in self.pages:
            size = self._path(p).stat().st_size
            self.assertLess(size, build_og.MAX_BYTES,
                            "%s весит %d КБ" % (p.slug, size // 1024))

    def test_pictures_differ_from_each_other(self):
        digests = []
        for p in self.pages:
            with open(self._path(p), "rb") as fh:
                digests.append(hashlib.sha256(fh.read()).hexdigest())
        for a, b in itertools.combinations(digests, 2):
            self.assertNotEqual(a, b, "две страницы получили одну и ту же картинку")

    def test_text_actually_landed_on_the_picture(self):
        # Если шрифт не нашёлся, Pillow молча нарисует пустое поле.
        # Значит на картинке обязаны быть и белые, и жёлтые пиксели.
        img = build_og.render(self.pages[0]).convert("RGB")
        colours = img.getcolors(maxcolors=200000) or []
        whites = sum(n for n, c in colours if min(c) > 200)
        yellows = sum(n for n, c in colours if c[0] > 200 and c[1] > 150 and c[2] < 110)
        self.assertGreater(whites, 3000, "белого текста на картинке нет")
        self.assertGreater(yellows, 3000, "жёлтого на картинке нет")

    def test_caption_fits_without_spilling_off_the_card(self):
        for p in self.pages:
            lines = build_og.wrap(p.caption, 700, 86, build_og.TEXT_WIDTH)
            self.assertLessEqual(len(lines), 3, "%s: подпись не влезает в три строки" % p.slug)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Шаг 2: Запустить тест и убедиться, что он падает**

```bash
cd ~/Progects/dostavka-ikonki && python3 -m unittest tests.test_og -v
```

Ожидается: `ImportError: cannot import name 'build_og'`.

- [ ] **Шаг 3: Написать `tools/build_og.py`**

```python
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

    # Подпись — главное, что видно в карточке.
    y = 244
    for line in wrap(page.caption, 700, 86, TEXT_WIDTH)[:3]:
        d.text((MARGIN, y), line, font=font(700, 86), fill="#FFFFFF")
        y += 98

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
```

- [ ] **Шаг 4: Запустить тесты и убедиться, что они проходят**

```bash
cd ~/Progects/dostavka-ikonki && python3 -m unittest discover -s tests -v
```

Ожидается: все тесты OK.

Если `test_caption_fits_without_spilling_off_the_card` падает — укоротить подпись в `content/pages.tsv`, а не уменьшать кегль: мелкая подпись в карточке чата не читается.

- [ ] **Шаг 5: Посмотреть на картинки глазами**

```bash
cd ~/Progects/dostavka-ikonki && open icons/og/index.png icons/og/track.png icons/og/promo.png
```

Проверить: текст не налезает на нижнюю подпись, знак не обрезан, три картинки заметно разные.

- [ ] **Шаг 6: Коммит**

```bash
cd ~/Progects/dostavka-ikonki && git add tools/build_og.py tests/test_og.py icons/og && git commit -m "Превью 1200x630: своё у каждой из трёх страниц

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Задача 5: Три страницы и подстановка тегов в шапку

**Файлы:**
- Создать: `index.html`, `track.html`, `promo.html`
- Создать: `styles.css`
- Создать: `tools/build_heads.py`
- Создать: `tests/test_heads.py`

**Интерфейсы:**
- Потребляет: `pages.load()`, `pages.SITE_NAME`, `pages.BASE_URL`, `mark.FIELD`.
- Отдаёт наружу:
  - `build_heads.BEGIN = "<!-- head:begin -->"`, `build_heads.END = "<!-- head:end -->"`
  - `build_heads.head_html(page) -> str` — содержимое шапки, без самих меток
  - `build_heads.inject(document: str, block: str) -> str` — подставляет блок между метками, метки оставляет на месте
  - `build_heads.main() -> None` — переписывает шапку у всех трёх страниц

- [ ] **Шаг 1: Написать падающий тест**

Создать `tests/test_heads.py`:

```python
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import build_heads, pages


class TestInject(unittest.TestCase):
    def test_replaces_only_between_the_marks(self):
        doc = "A\n%s\nстарое\n%s\nB" % (build_heads.BEGIN, build_heads.END)
        out = build_heads.inject(doc, "новое")
        self.assertIn("новое", out)
        self.assertNotIn("старое", out)
        self.assertTrue(out.startswith("A"))
        self.assertTrue(out.endswith("B"))
        self.assertIn(build_heads.BEGIN, out)
        self.assertIn(build_heads.END, out)

    def test_running_twice_changes_nothing(self):
        doc = "A\n%s\n\n%s\nB" % (build_heads.BEGIN, build_heads.END)
        once = build_heads.inject(doc, "новое")
        self.assertEqual(once, build_heads.inject(once, "новое"))

    def test_missing_marks_are_an_error_not_silence(self):
        with self.assertRaises(ValueError):
            build_heads.inject("<html></html>", "новое")


class TestHeadHtml(unittest.TestCase):
    def setUp(self):
        self.pages = pages.load()
        self.heads = {p.slug: build_heads.head_html(p) for p in self.pages}

    def test_preview_address_is_absolute(self):
        for slug, head in self.heads.items():
            found = re.findall(r'property="og:image" content="([^"]+)"', head)
            self.assertEqual(len(found), 1, slug)
            self.assertTrue(found[0].startswith("https://"), "%s: %s" % (slug, found[0]))

    def test_site_name_is_not_the_title(self):
        for slug, head in self.heads.items():
            title = re.search(r'property="og:title" content="([^"]+)"', head).group(1)
            name = re.search(r'property="og:site_name" content="([^"]+)"', head).group(1)
            self.assertNotEqual(title.lower(), name.lower(), slug)

    def test_every_page_has_its_own_canonical(self):
        canons = []
        for p in self.pages:
            found = re.search(r'rel="canonical" href="([^"]+)"', self.heads[p.slug])
            self.assertIsNotNone(found, p.slug)
            canons.append(found.group(1))
        self.assertEqual(len(set(canons)), len(canons))

    def test_closed_from_search_engines(self):
        for slug, head in self.heads.items():
            self.assertIn('name="robots" content="noindex, nofollow"', head, slug)

    def test_declares_the_whole_icon_set(self):
        for slug, head in self.heads.items():
            for needle in (
                'icons/favicon.svg',
                'icons/favicon.ico',
                'icons/apple-touch-icon.png',
                'rel="manifest"',
                'name="theme-color"',
            ):
                self.assertIn(needle, head, "%s: нет %s" % (slug, needle))

    def test_card_size_is_declared(self):
        for slug, head in self.heads.items():
            self.assertIn('property="og:image:width" content="1200"', head, slug)
            self.assertIn('property="og:image:height" content="630"', head, slug)

    def test_no_external_requests(self):
        for slug, head in self.heads.items():
            external = re.findall(r'(?:href|src)="(https?://[^"]+)"', head)
            self.assertEqual(external, [], "%s ходит наружу: %s" % (slug, external))


class TestBuiltPages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build_heads.main()

    def test_each_file_got_its_own_head(self):
        for p in pages.load():
            text = (pages.ROOT / p.file_name).read_text(encoding="utf-8")
            self.assertIn(p.og_image_url, text, p.slug)
            self.assertIn(p.title, text, p.slug)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Шаг 2: Запустить тест и убедиться, что он падает**

```bash
cd ~/Progects/dostavka-ikonki && python3 -m unittest tests.test_heads -v
```

Ожидается: `ImportError: cannot import name 'build_heads'`.

- [ ] **Шаг 3: Написать `tools/build_heads.py`**

```python
"""Шапка страницы собирается из content/pages.tsv и подставляется на место.

Между метками head:begin и head:end страница принадлежит скрипту. Всё
остальное — обычный HTML, который правится руками.
"""

import html

from tools import mark, pages

BEGIN = "<!-- head:begin -->"
END = "<!-- head:end -->"


def _meta(kind, key, value):
    return '  <meta %s="%s" content="%s">' % (kind, key, html.escape(value, quote=True))


def head_html(page):
    """Содержимое шапки для одной страницы, без самих меток."""
    title = page.title
    desc = page.description
    rows = [
        '  <meta charset="utf-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1">',
        '  <title>%s — %s</title>' % (html.escape(title), html.escape(pages.SITE_NAME)),
        _meta("name", "description", desc),
        _meta("name", "robots", "noindex, nofollow"),
        '  <link rel="canonical" href="%s">' % page.url,
        '',
        '  <link rel="icon" href="icons/favicon.svg" type="image/svg+xml">',
        '  <link rel="icon" href="icons/favicon.ico" sizes="16x16 32x32 48x48">',
        '  <link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">',
        '  <link rel="apple-touch-icon" sizes="180x180" href="icons/apple-touch-icon.png">',
        '  <link rel="manifest" href="site.webmanifest">',
        _meta("name", "theme-color", mark.FIELD),
        '',
        _meta("property", "og:type", "website"),
        _meta("property", "og:site_name", pages.SITE_NAME),
        _meta("property", "og:locale", "ru_RU"),
        _meta("property", "og:title", title),
        _meta("property", "og:description", desc),
        '  <meta property="og:url" content="%s">' % page.url,
        '  <meta property="og:image" content="%s">' % page.og_image_url,
        _meta("property", "og:image:width", "1200"),
        _meta("property", "og:image:height", "630"),
        _meta("property", "og:image:type", "image/png"),
        _meta("property", "og:image:alt", page.caption),
        '',
        _meta("name", "twitter:card", "summary_large_image"),
        _meta("name", "twitter:title", title),
        _meta("name", "twitter:description", desc),
        '  <meta name="twitter:image" content="%s">' % page.og_image_url,
        '',
        '  <link rel="stylesheet" href="styles.css">',
    ]
    return "\n".join(rows)


def inject(document, block):
    start = document.find(BEGIN)
    end = document.find(END)
    if start < 0 or end < 0 or end < start:
        raise ValueError("в файле нет меток %s и %s" % (BEGIN, END))
    return document[:start + len(BEGIN)] + "\n" + block + "\n" + document[end:]


def main():
    for page in pages.load():
        path = pages.ROOT / page.file_name
        text = path.read_text(encoding="utf-8")
        path.write_text(inject(text, head_html(page)), encoding="utf-8")
        print("шапка обновлена: %s" % page.file_name)


if __name__ == "__main__":
    main()
```

- [ ] **Шаг 4: Написать `index.html`**

Вёрстка намеренно простая: предмет работы — шапка документа и файлы картинок, а не блоки на странице. Участок между метками не трогать руками, его перепишет скрипт.

```html
<!doctype html>
<html lang="ru">
<head>
<!-- head:begin -->
<!-- head:end -->
</head>
<body>
<p class="disclaimer">Демонстрационная работа. Компания «Прямиком», телефоны и
адреса вымышлены. Заказ оформить нельзя, данные не собираются.</p>

<header class="top">
  <a class="brand" href="index.html">
    <img src="icons/icon-48.png" width="40" height="40" alt="">
    <span>Прямиком</span>
  </a>
  <nav>
    <a href="index.html" aria-current="page">Главная</a>
    <a href="track.html">Отследить заказ</a>
    <a href="promo.html">Акция</a>
    <a href="showcase.html">Как выглядит ссылка</a>
  </nav>
</header>

<main>
  <h1>Доставка посылок и еды по городу за 90 минут</h1>
  <p class="lead">Курьер забирает у двери и привозит по адресу в тот же день:
  документы, посылки, заказ из кафе.</p>

  <ul class="cards">
    <li><h2>Забираем у двери</h2><p>Курьер приезжает в течение получаса после
    заявки и забирает отправление прямо из рук.</p></li>
    <li><h2>90 минут по городу</h2><p>В пределах города — полтора часа.
    За город считаем отдельно по километрам.</p></li>
    <li><h2>Видно, где посылка</h2><p>По номеру накладной видно, на каком этапе
    отправление и во сколько его ждать.</p></li>
  </ul>

  <p class="note">Условный телефон для примера: +7 000 000-00-00.
  Звонить по нему некуда.</p>
</main>

<footer>
  <p>«Прямиком» — вымышленная служба доставки. Страница сделана, чтобы показать
  значок сайта и превью ссылки в мессенджерах.</p>
  <p><a href="showcase.html">Посмотреть, как ссылка разворачивается в чате</a></p>
</footer>
</body>
</html>
```

- [ ] **Шаг 5: Написать `track.html`**

Отслеживание ненастоящее, и на странице это сказано прямым текстом. Поле ввода ничего никуда не отправляет: скрипт на странице просто показывает заранее заданное состояние.

```html
<!doctype html>
<html lang="ru">
<head>
<!-- head:begin -->
<!-- head:end -->
</head>
<body>
<p class="disclaimer">Демонстрационная работа. Отслеживание ненастоящее: номер
можно ввести любой, состояние показывается заранее заданное. Данные никуда
не отправляются и нигде не сохраняются.</p>

<header class="top">
  <a class="brand" href="index.html">
    <img src="icons/icon-48.png" width="40" height="40" alt="">
    <span>Прямиком</span>
  </a>
  <nav>
    <a href="index.html">Главная</a>
    <a href="track.html" aria-current="page">Отследить заказ</a>
    <a href="promo.html">Акция</a>
    <a href="showcase.html">Как выглядит ссылка</a>
  </nav>
</header>

<main>
  <h1>Где сейчас мой заказ</h1>
  <p class="lead">Введите номер накладной и посмотрите, на каком этапе посылка
  и во сколько её ждать сегодня.</p>

  <div class="track">
    <label for="code">Номер накладной</label>
    <input id="code" type="text" inputmode="numeric" placeholder="например, 4417"
           autocomplete="off">
    <button id="go" type="button">Показать</button>
  </div>

  <ol class="steps" id="steps" hidden>
    <li class="done">Заявка принята — 10:05</li>
    <li class="done">Курьер забрал отправление — 10:38</li>
    <li class="now">В пути по городу — сейчас</li>
    <li>Вручено получателю — ожидается к 11:35</li>
  </ol>

  <p class="note" id="hint">Состояние показывается одно и то же для любого
  номера: это демонстрация, а не работающая служба.</p>
</main>

<footer>
  <p>«Прямиком» — вымышленная служба доставки.</p>
  <p><a href="showcase.html">Посмотреть, как ссылка разворачивается в чате</a></p>
</footer>

<script>
  document.getElementById('go').addEventListener('click', function () {
    document.getElementById('steps').hidden = false;
  });
</script>
</body>
</html>
```

- [ ] **Шаг 6: Написать `promo.html`**

```html
<!doctype html>
<html lang="ru">
<head>
<!-- head:begin -->
<!-- head:end -->
</head>
<body>
<p class="disclaimer">Демонстрационная работа. Акции не существует, компания
вымышлена, заявку оставить нельзя.</p>

<header class="top">
  <a class="brand" href="index.html">
    <img src="icons/icon-48.png" width="40" height="40" alt="">
    <span>Прямиком</span>
  </a>
  <nav>
    <a href="index.html">Главная</a>
    <a href="track.html">Отследить заказ</a>
    <a href="promo.html" aria-current="page">Акция</a>
    <a href="showcase.html">Как выглядит ссылка</a>
  </nav>
</header>

<main>
  <h1>Первая доставка за 1 рубль</h1>
  <p class="lead">До 30 октября новый клиент платит рубль за первую доставку
  по городу. Один заказ на один телефон.</p>

  <ul class="cards">
    <li><h2>Кому</h2><p>Тем, кто раньше не заказывал доставку в «Прямиком».</p></li>
    <li><h2>До какого числа</h2><p>Заявка должна быть оформлена до 30 октября
    включительно.</p></li>
    <li><h2>Что не входит</h2><p>Доставка за город и отправления тяжелее
    пяти килограммов считаются по обычному тарифу.</p></li>
  </ul>

  <p class="note">Это страница-пример. Именно такую в жизни пересылают в чат
  отдельной ссылкой — и именно поэтому у неё своё превью, а не общее по сайту.</p>
</main>

<footer>
  <p>«Прямиком» — вымышленная служба доставки.</p>
  <p><a href="showcase.html">Посмотреть, как ссылка разворачивается в чате</a></p>
</footer>
</body>
</html>
```

- [ ] **Шаг 7: Написать `styles.css`**

Шрифт подключается своим файлом, без обращения наружу. `font-display: swap`, чтобы текст не пропадал на время загрузки.

```css
@font-face {
  font-family: "PT Sans Local";
  src: url("fonts/ptsans-400.woff2") format("woff2");
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: "PT Sans Local";
  src: url("fonts/ptsans-700.woff2") format("woff2");
  font-weight: 700;
  font-style: normal;
  font-display: swap;
}

:root {
  --field: #0A2A66;
  --arrow: #FFC61A;
  --ink: #12203a;
  --muted: #5b6b88;
  --line: #dde3ee;
  --paper: #ffffff;
  --shade: #f4f6fb;
}

* { box-sizing: border-box; }

html { -webkit-text-size-adjust: 100%; }

body {
  margin: 0;
  font-family: "PT Sans Local", system-ui, sans-serif;
  font-size: 17px;
  line-height: 1.55;
  color: var(--ink);
  background: var(--paper);
}

.disclaimer {
  margin: 0;
  padding: 10px 16px;
  background: #fff5d6;
  border-bottom: 1px solid #efd98a;
  font-size: 14px;
  color: #6a5312;
}

.top {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 24px;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--line);
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  font-size: 20px;
  color: var(--field);
  text-decoration: none;
}

.top nav { display: flex; flex-wrap: wrap; gap: 8px 18px; }
.top nav a { color: var(--muted); text-decoration: none; }
.top nav a:hover { color: var(--field); text-decoration: underline; }
.top nav a[aria-current="page"] { color: var(--field); font-weight: 700; }

main { max-width: 860px; margin: 0 auto; padding: 28px 16px 8px; }

h1 { font-size: 34px; line-height: 1.2; margin: 8px 0 12px; color: var(--field); }
h2 { font-size: 19px; margin: 0 0 6px; }

.lead { font-size: 19px; color: var(--muted); margin: 0 0 28px; }

.cards {
  list-style: none;
  margin: 0 0 28px;
  padding: 0;
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
}
.cards li {
  background: var(--shade);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 16px;
}
.cards p { margin: 0; color: var(--muted); font-size: 16px; }

.note { color: var(--muted); font-size: 15px; }

.track { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-bottom: 20px; }
.track label { width: 100%; font-weight: 700; }
.track input {
  flex: 1 1 200px;
  min-width: 0;
  padding: 11px 13px;
  font: inherit;
  border: 1px solid var(--line);
  border-radius: 10px;
}
.track button {
  padding: 11px 20px;
  font: inherit;
  font-weight: 700;
  color: var(--field);
  background: var(--arrow);
  border: 0;
  border-radius: 10px;
  cursor: pointer;
}
.track button:hover { filter: brightness(0.94); }

.steps { margin: 0 0 20px; padding-left: 22px; }
.steps li { margin-bottom: 6px; color: var(--muted); }
.steps li.done { color: var(--ink); }
.steps li.now { color: var(--field); font-weight: 700; }

footer {
  max-width: 860px;
  margin: 24px auto 0;
  padding: 18px 16px 40px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 15px;
}
footer a { color: var(--field); }

@media (max-width: 420px) {
  h1 { font-size: 27px; }
  .lead { font-size: 17px; }
}
```

- [ ] **Шаг 8: Запустить сборку шапок и тесты**

```bash
cd ~/Progects/dostavka-ikonki && python3 -m tools.build_heads && python3 -m unittest discover -s tests -v
```

Ожидается: три строки «шапка обновлена» и все тесты OK.

- [ ] **Шаг 9: Коммит**

```bash
cd ~/Progects/dostavka-ikonki && git add index.html track.html promo.html styles.css tools/build_heads.py tests/test_heads.py && git commit -m "Три страницы и подстановка мета-тегов в шапку из одного источника

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---
## Задача 6: Манифест, robots.txt и сборка одной командой

**Файлы:**
- Создать: `tools/build_manifest.py`
- Создать: `tools/build.py`
- Создать: `robots.txt`
- Создать: `.nojekyll`
- Создаёт на диске: `site.webmanifest`

**Интерфейсы:**
- Потребляет: `pages.SITE_NAME`, `pages.ROOT`, `mark.FIELD`.
- Отдаёт наружу:
  - `build_manifest.manifest() -> dict`
  - `build_manifest.main() -> None`
  - `build.main() -> None` — вся сборка в правильном порядке

- [ ] **Шаг 1: Написать `tools/build_manifest.py`**

```python
"""site.webmanifest кладётся ради одного: чтобы на домашнем экране Android
появился значок, а не обрезанный снимок страницы.

Ни офлайнового режима, ни установки приложением в работе нет, поэтому
display стоит browser — обещать то, чего не делаем, нельзя.
"""

import json

from tools import mark, pages

ICONS = (192, 512)


def manifest():
    return {
        "name": "%s — доставка по городу" % pages.SITE_NAME,
        "short_name": pages.SITE_NAME,
        "lang": "ru",
        "dir": "ltr",
        "start_url": "./index.html",
        "scope": "./",
        "display": "browser",
        "background_color": mark.FIELD,
        "theme_color": mark.FIELD,
        "icons": [
            {
                "src": "icons/icon-%d.png" % size,
                "sizes": "%dx%d" % (size, size),
                "type": "image/png",
            }
            for size in ICONS
        ],
    }


def main():
    path = pages.ROOT / "site.webmanifest"
    path.write_text(
        json.dumps(manifest(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("манифест записан: %s" % path.name)


if __name__ == "__main__":
    main()
```

- [ ] **Шаг 2: Написать `robots.txt`**

Это та самая ловушка из спеки. Комментарий в файле нужен, чтобы через полгода никто не «навёл порядок», закрыв сайт целиком.

```
# Демонстрационный сайт закрыт от поисковиков мета-тегом noindex на каждой
# странице. Глухого Disallow здесь нет намеренно: боты мессенджеров читают
# robots.txt, и запрет оставил бы работу про превью ссылок без превью.

User-agent: *
Allow: /
```

- [ ] **Шаг 3: Создать `.nojekyll`**

GitHub Pages по умолчанию прогоняет содержимое через Jekyll и выбрасывает файлы и папки, начинающиеся с подчёркивания. Пустой файл `.nojekyll` это отключает.

```bash
cd ~/Progects/dostavka-ikonki && touch .nojekyll
```

- [ ] **Шаг 4: Написать `tools/build.py`**

```python
"""Вся сборка одной командой: python3 -m tools.build

Порядок важен: шрифт нужен картинкам превью, а картинки должны существовать
до того, как проверки начнут искать их на диске.
"""

from tools import build_font, build_heads, build_icons, build_manifest, build_og


def main():
    build_font.main()
    build_icons.main()
    build_og.main()
    build_manifest.main()
    build_heads.main()
    print("сборка готова")


if __name__ == "__main__":
    main()
```

- [ ] **Шаг 5: Собрать всё и убедиться, что тесты проходят**

```bash
cd ~/Progects/dostavka-ikonki && python3 -m tools.build && python3 -m unittest discover -s tests -v
```

Ожидается: сборка проходит без ошибок, все тесты OK.

- [ ] **Шаг 6: Коммит**

```bash
cd ~/Progects/dostavka-ikonki && git add tools/build_manifest.py tools/build.py robots.txt .nojekyll site.webmanifest && git commit -m "Манифест ради значка на домашнем экране, robots.txt без глухого запрета, сборка одной командой

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Задача 7: Проверки — пять ошибок ловятся скриптом

**Файлы:**
- Создать: `tools/check.py`
- Создать: `tests/test_check.py`

**Интерфейсы:**
- Потребляет: `pages.load()`, `pages.ROOT`, `pages.BASE_URL`, `pages.SITE_NAME`, `mark.contrast`, `build_og.MAX_BYTES`.
- Отдаёт наружу:
  - `check.parse_head(text) -> Head` с полями `metas`, `links`, `title`
  - `check.meta_value(head, key) -> str | None`
  - `check.check_files(root=None) -> list[str]` — проверки по файлам на диске
  - `check.check_live(base_url) -> list[str]` — проверки по живому адресу
  - `check.main(argv) -> int` — код возврата 0, если проблем нет

- [ ] **Шаг 1: Написать падающий тест**

Создать `tests/test_check.py`:

```python
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image

from tools import check, pages


def copy_site(dest):
    """Копия готового сайта, на которой можно ломать что угодно."""
    for name in ("index.html", "track.html", "promo.html", "showcase.html",
                 "styles.css", "site.webmanifest", "robots.txt"):
        src = pages.ROOT / name
        if src.exists():
            shutil.copy2(src, dest / name)
    shutil.copytree(pages.ROOT / "icons", dest / "icons")
    shutil.copytree(pages.ROOT / "fonts", dest / "fonts")
    return dest


class CheckCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        copy_site(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def problems(self):
        return check.check_files(self.tmp)

    def assertComplains(self, needle):
        found = self.problems()
        self.assertTrue(
            any(needle in p for p in found),
            "проверка промолчала про %r, а нашла только: %s" % (needle, found),
        )


class TestCleanSite(CheckCase):
    def test_собранный_сайт_проходит_проверку(self):
        self.assertEqual(self.problems(), [])


class TestFiveMistakes(CheckCase):
    def test_относительный_адрес_картинки_превью(self):
        p = self.tmp / "index.html"
        text = p.read_text(encoding="utf-8")
        text = text.replace(
            'property="og:image" content="%s"' % pages.load()[0].og_image_url,
            'property="og:image" content="icons/og/index.png"',
        )
        p.write_text(text, encoding="utf-8")
        self.assertComplains("не абсолютный")

    def test_объявленного_файла_нет(self):
        (self.tmp / "icons" / "apple-touch-icon.png").unlink()
        self.assertComplains("apple-touch-icon.png")

    def test_название_сайта_повторяет_заголовок(self):
        p = self.tmp / "promo.html"
        text = p.read_text(encoding="utf-8")
        text = text.replace(
            'property="og:site_name" content="%s"' % pages.SITE_NAME,
            'property="og:site_name" content="Первая доставка за 1 рубль"',
        )
        p.write_text(text, encoding="utf-8")
        self.assertComplains("повторяет заголовок")

    def test_одна_картинка_на_весь_сайт(self):
        first = pages.load()[0].og_image_url
        p = self.tmp / "promo.html"
        text = p.read_text(encoding="utf-8")
        text = text.replace(pages.load()[2].og_image_url, first)
        p.write_text(text, encoding="utf-8")
        self.assertComplains("повторяется")

    def test_размер_файла_расходится_с_именем(self):
        path = self.tmp / "icons" / "icon-32.png"
        with Image.open(path) as img:
            img.resize((30, 30)).save(path)
        self.assertComplains("icon-32.png")


class TestOtherTraps(CheckCase):
    def test_глухой_запрет_в_robots(self):
        (self.tmp / "robots.txt").write_text(
            "User-agent: *\nDisallow: /\n", encoding="utf-8"
        )
        self.assertComplains("Disallow")

    def test_страница_не_закрыта_от_поисковиков(self):
        p = self.tmp / "track.html"
        text = p.read_text(encoding="utf-8")
        text = text.replace('content="noindex, nofollow"', 'content="all"')
        p.write_text(text, encoding="utf-8")
        self.assertComplains("noindex")

    def test_картинка_превью_слишком_тяжёлая(self):
        path = self.tmp / "icons" / "og" / "track.png"
        with open(path, "ab") as fh:
            fh.write(b"\0" * (310 * 1024))
        self.assertComplains("тяжелее")

    def test_манифест_обещает_несуществующий_значок(self):
        (self.tmp / "icons" / "icon-512.png").unlink()
        self.assertComplains("icon-512.png")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Шаг 2: Запустить тест и убедиться, что он падает**

```bash
cd ~/Progects/dostavka-ikonki && python3 -m unittest tests.test_check -v
```

Ожидается: `ImportError: cannot import name 'check'`.

- [ ] **Шаг 3: Написать `tools/check.py`**

```python
"""Проверки комплекта: пять частых ошибок ловятся здесь, а не на глаз.

check_files — по файлам на диске, годится до выкладки.
check_live — по живому адресу, годится после.
"""

import json
import pathlib
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser

from PIL import Image

from tools import build_og, mark, pages

ICON_RELS = ("icon", "shortcut icon", "apple-touch-icon", "manifest")
AGENT = "dostavka-ikonki-check/1.0"


class Head(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.metas = []
        self.links = []
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "meta":
            self.metas.append(data)
        elif tag == "link":
            self.links.append(data)
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def parse_head(text):
    head = Head()
    head.feed(text)
    return head


def meta_value(head, key):
    for item in head.metas:
        if item.get("property") == key or item.get("name") == key:
            return item.get("content")
    return None


def _declared_files(head):
    """Пути, объявленные в шапке: значки и манифест. Только относительные."""
    out = []
    for link in head.links:
        rel = (link.get("rel") or "").lower()
        href = link.get("href") or ""
        if rel in ICON_RELS and not href.startswith("http"):
            out.append((href, link.get("sizes")))
    return out


def _check_png_side(root, href, declared_sizes, where, add):
    path = root / href
    if path.suffix.lower() != ".png":
        return
    with Image.open(path) as img:
        width, height = img.size
    if width != height:
        add("%s: %s не квадратный — %dx%d" % (where, href, width, height))
        return
    stem = path.stem
    if "-" in stem and stem.rsplit("-", 1)[1].isdigit():
        promised = int(stem.rsplit("-", 1)[1])
        if promised != width:
            add("%s: %s внутри %d пикселей, а имя обещает %d"
                % (where, href, width, promised))
    if declared_sizes:
        wanted = {int(s.split("x")[0]) for s in declared_sizes.split() if "x" in s}
        if wanted and width not in wanted:
            add("%s: %s внутри %d пикселей, а в теге написано %s"
                % (where, href, width, declared_sizes))


def check_files(root=None):
    """Проблемы, которые видно по файлам. Пустой список — всё хорошо."""
    root = pathlib.Path(root or pages.ROOT)
    problems = []
    add = problems.append

    ratio = mark.contrast(mark.FIELD, mark.ARROW)
    if ratio < 4.5:
        add("контраст цветов знака %.2f:1 — ниже порога 4.5:1" % ratio)

    site = pages.load()
    titles, descriptions, images, canonicals = {}, {}, {}, {}

    for page in site:
        path = root / page.file_name
        where = page.file_name
        if not path.exists():
            add("%s: страницы нет на диске" % where)
            continue
        head = parse_head(path.read_text(encoding="utf-8"))

        robots = meta_value(head, "robots") or ""
        if "noindex" not in robots:
            add("%s: нет noindex — вымышленная компания попадёт в поиск" % where)

        title = meta_value(head, "og:title") or ""
        name = meta_value(head, "og:site_name") or ""
        description = meta_value(head, "og:description") or ""
        image = meta_value(head, "og:image") or ""

        if not title:
            add("%s: нет og:title" % where)
        if not description:
            add("%s: нет og:description" % where)
        if title and name and title.strip().lower() == name.strip().lower():
            add("%s: название сайта повторяет заголовок — в карточке будут "
                "две одинаковые строки" % where)

        if not image:
            add("%s: нет og:image" % where)
        elif not image.startswith("https://"):
            add("%s: адрес картинки превью не абсолютный (%s) — мессенджер "
                "не подставит домен и карточка придёт без картинки" % (where, image))
        else:
            rel = image[len(pages.BASE_URL):] if image.startswith(pages.BASE_URL) else None
            if rel is None:
                add("%s: картинка превью лежит не на этом сайте: %s" % (where, image))
            else:
                img_path = root / rel
                if not img_path.exists():
                    add("%s: объявлена картинка %s, а файла нет" % (where, rel))
                else:
                    with Image.open(img_path) as opened:
                        size = opened.size
                    if size != build_og.CARD:
                        add("%s: картинка %s размером %dx%d вместо 1200x630"
                            % (where, rel, size[0], size[1]))
                    weight = img_path.stat().st_size
                    if weight >= build_og.MAX_BYTES:
                        add("%s: картинка %s тяжелее 300 КБ (%d КБ) — WhatsApp "
                            "такую пропустит" % (where, rel, weight // 1024))

        canonical = None
        for link in head.links:
            if (link.get("rel") or "").lower() == "canonical":
                canonical = link.get("href")
        if not canonical:
            add("%s: нет canonical" % where)
        elif not canonical.startswith("https://"):
            add("%s: canonical не абсолютный: %s" % (where, canonical))

        for field, store, value in (
            ("заголовок", titles, title),
            ("описание", descriptions, description),
            ("картинка превью", images, image),
            ("canonical", canonicals, canonical),
        ):
            if not value:
                continue
            if value in store:
                add("%s: %s повторяется со страницей %s — в чате обе ссылки "
                    "развернутся одинаково" % (where, field, store[value]))
            else:
                store[value] = where

        for href, sizes in _declared_files(head):
            declared = root / href
            if not declared.exists():
                add("%s: в шапке объявлен %s, а по этому адресу ничего нет"
                    % (where, href))
                continue
            _check_png_side(root, href, sizes, where, add)

    problems.extend(_check_manifest(root))
    problems.extend(_check_robots(root))
    problems.extend(_check_icon_names(root))
    return problems


def _check_manifest(root):
    problems = []
    path = root / "site.webmanifest"
    if not path.exists():
        return ["site.webmanifest: файла нет"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as err:
        return ["site.webmanifest: не разбирается как JSON (%s)" % err]
    for icon in data.get("icons", []):
        src = icon.get("src", "")
        target = root / src
        if not target.exists():
            problems.append("site.webmanifest: обещан значок %s, а файла нет" % src)
            continue
        with Image.open(target) as img:
            width = img.size[0]
        promised = icon.get("sizes", "")
        if promised and width != int(promised.split("x")[0]):
            problems.append("site.webmanifest: %s внутри %d пикселей, а заявлен как %s"
                            % (src, width, promised))
    return problems


def _check_robots(root):
    path = root / "robots.txt"
    if not path.exists():
        return []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.split("#")[0].strip()
        if stripped.lower().replace(" ", "") == "disallow:/":
            return ["robots.txt: глухой Disallow закроет сайт и от ботов "
                    "мессенджеров — карточка не соберётся"]
    return []


def _check_icon_names(root):
    """Каждый файл icon-N.png должен быть ровно N пикселей в стороне —
    даже тот, который сейчас нигде в шапке не объявлен. Иначе расхождение
    всплывёт ровно тогда, когда файл кому-нибудь понадобится."""
    problems = []
    folder = root / "icons"
    if not folder.exists():
        return ["папки icons нет"]
    for path in sorted(folder.glob("icon-*.png")):
        stem = path.stem.rsplit("-", 1)[1]
        if not stem.isdigit():
            continue
        promised = int(stem)
        with Image.open(path) as img:
            width, height = img.size
        if (width, height) != (promised, promised):
            problems.append("icons/%s внутри %dx%d, а имя обещает %d"
                            % (path.name, width, height, promised))
    return problems


def _fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": AGENT})
    return urllib.request.urlopen(request, timeout=20)


def check_live(base_url):
    """Проверки по живому адресу: каждый объявленный файл действительно
    отдаётся. На диске файл может лежать, а Pages его не раздавать."""
    problems = []
    base = base_url if base_url.endswith("/") else base_url + "/"
    for page in pages.load():
        url = base if page.slug == "index" else base + page.file_name
        try:
            response = _fetch(url)
        except urllib.error.HTTPError as err:
            problems.append("%s отдаёт %s" % (url, err.code))
            continue
        except urllib.error.URLError as err:
            problems.append("%s недоступен: %s" % (url, err.reason))
            continue
        head = parse_head(response.read().decode("utf-8", "replace"))

        targets = [meta_value(head, "og:image"), meta_value(head, "twitter:image")]
        targets += [base + href for href, _ in _declared_files(head)]
        for target in targets:
            if not target:
                continue
            try:
                got = _fetch(target)
            except urllib.error.HTTPError as err:
                problems.append("%s: %s отдаёт %s" % (page.file_name, target, err.code))
                continue
            except urllib.error.URLError as err:
                problems.append("%s: %s недоступен: %s" % (page.file_name, target, err.reason))
                continue
            if got.status != 200:
                problems.append("%s: %s отдаёт %s" % (page.file_name, target, got.status))

    try:
        robots = _fetch(base + "robots.txt").read().decode("utf-8", "replace")
        for line in robots.splitlines():
            if line.split("#")[0].strip().lower().replace(" ", "") == "disallow:/":
                problems.append("robots.txt на живом адресе закрывает сайт целиком")
    except urllib.error.URLError:
        pass
    return problems


def main(argv=None):
    argv = list(argv if argv is not None else sys.argv[1:])
    problems = check_files()
    if argv and argv[0] == "--live":
        base = argv[1] if len(argv) > 1 else pages.BASE_URL
        print("проверяю живой адрес: %s" % base)
        problems += check_live(base)

    if problems:
        print("Нашлось %d:" % len(problems))
        for item in problems:
            print("  · %s" % item)
        return 1
    print("Проверки пройдены, замечаний нет.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Шаг 4: Запустить тесты и убедиться, что они проходят**

`showcase.html` ещё не существует — `copy_site` его просто пропустит, это предусмотрено.

```bash
cd ~/Progects/dostavka-ikonki && python3 -m unittest discover -s tests -v
```

Ожидается: все тесты OK. Особое внимание на `test_собранный_сайт_проходит_проверку`: если он падает — чинить сайт, а не ослаблять проверку.

- [ ] **Шаг 5: Прогнать проверку по настоящему сайту**

```bash
cd ~/Progects/dostavka-ikonki && python3 -m tools.check
```

Ожидается: `Проверки пройдены, замечаний нет.`

- [ ] **Шаг 6: Коммит**

```bash
cd ~/Progects/dostavka-ikonki && git add tools/check.py tests/test_check.py && git commit -m "Проверки: пять частых ошибок ловятся скриптом, а не на глаз

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---
## Задача 8: Витрина — карточки из живых тегов

Главное правило витрины: в ней нет ни одного написанного руками заголовка. Она запрашивает живые страницы того же сайта, разбирает их шапку и строит карточки из того, что нашла. Разойтись с действительностью она не может: разойтись — значит показать пустое место.

**Файлы:**
- Создать: `showcase.html`
- Изменить: `styles.css` (дописать блок стилей витрины в конец)
- Изменить: `tools/check.py` (добавить `EXTRA_PAGES` и сверку цветов в CSS)
- Изменить: `tests/test_check.py` (два новых теста)

**Интерфейсы:**
- Потребляет: `icons/*`, три готовые страницы, `styles.css`.
- Отдаёт наружу: `check.EXTRA_PAGES = ("showcase.html",)`, `check._check_colours(root) -> list[str]`.

- [ ] **Шаг 1: Написать `showcase.html`**

```html
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Как ссылка выглядит в чате — Прямиком</title>
  <meta name="description" content="Карточки собраны из живых тегов трёх страниц сайта и контактный лист значка в пяти размерах.">
  <meta name="robots" content="noindex, nofollow">
  <link rel="canonical" href="https://pyhphhddb8-eng.github.io/dostavka-ikonki/showcase.html">
  <link rel="icon" href="icons/favicon.svg" type="image/svg+xml">
  <link rel="icon" href="icons/favicon.ico" sizes="16x16 32x32 48x48">
  <link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">
  <link rel="apple-touch-icon" sizes="180x180" href="icons/apple-touch-icon.png">
  <link rel="manifest" href="site.webmanifest">
  <meta name="theme-color" content="#0A2A66">
  <link rel="stylesheet" href="styles.css">
</head>
<body>
<p class="disclaimer"><b>Это макет, а не снимок экрана из чата.</b> Карточки
ниже собраны прямо сейчас из тегов живых страниц этого сайта. Показать
настоящую переписку я не могу, а выдавать рисунок за скриншот нельзя.</p>

<header class="top">
  <a class="brand" href="index.html">
    <img src="icons/icon-48.png" width="40" height="40" alt="">
    <span>Прямиком</span>
  </a>
  <nav>
    <a href="index.html">Главная</a>
    <a href="track.html">Отследить заказ</a>
    <a href="promo.html">Акция</a>
    <a href="showcase.html" aria-current="page">Как выглядит ссылка</a>
  </nav>
</header>

<main>
  <h1>Как ссылка выглядит в чате</h1>
  <p class="lead">Три страницы сайта — три разные карточки. Ни один заголовок
  на этой странице не написан руками: всё прочитано из шапок живых страниц.</p>

  <div id="warning" class="warn" hidden></div>
  <div id="cards" class="cards-row">Читаю страницы…</div>

  <h2 class="section">Что проверено прямо сейчас</h2>
  <p class="note">Пять ошибок, которые в этой задаче делают чаще всего.
  Каждая проверяется, а не объявляется.</p>
  <ul id="checks" class="checks">Проверяю…</ul>

  <h2 class="section">Значок в настоящих размерах</h2>
  <p class="note">Слева направо: 16, 32, 48, 180 и 512 пикселей. 16 — это
  настоящий размер во вкладке браузера.</p>
  <div class="sheet light" id="sheet-light"></div>
  <div class="sheet dark" id="sheet-dark"></div>
  <p class="note">На светлой вкладке знак читается силуэтом синего поля, на
  тёмной работу берёт на себя жёлтая стрелка.</p>
</main>

<footer>
  <p>«Прямиком» — вымышленная служба доставки. Витрина строится из живых тегов
  страниц, поэтому разойтись с ними она не может.</p>
</footer>

<script>
const FILES = ['index.html', 'track.html', 'promo.html'];
const ICON_SIZES = [16, 32, 48, 180, 512];

function attr(doc, selector, name) {
  const node = doc.querySelector(selector);
  return node ? (node.getAttribute(name) || '') : '';
}

async function readPage(file) {
  const response = await fetch(file, { cache: 'no-store' });
  const doc = new DOMParser().parseFromString(await response.text(), 'text/html');
  const declared = [...doc.querySelectorAll('link[rel="icon"], link[rel="apple-touch-icon"], link[rel="manifest"]')]
    .map((node) => node.getAttribute('href'))
    .filter((href) => href && !/^https?:/.test(href));
  return {
    file: file,
    title: attr(doc, 'meta[property="og:title"]', 'content'),
    description: attr(doc, 'meta[property="og:description"]', 'content'),
    image: attr(doc, 'meta[property="og:image"]', 'content'),
    siteName: attr(doc, 'meta[property="og:site_name"]', 'content'),
    canonical: attr(doc, 'link[rel="canonical"]', 'href'),
    declared: declared
  };
}

function sameOrigin(url) {
  try { return new URL(url, location.href).origin === location.origin; }
  catch (e) { return false; }
}

function localCopy(url) {
  const at = url.indexOf('/icons/');
  return at < 0 ? url : url.slice(at + 1);
}

function host(url) {
  try { return new URL(url, location.href).host; } catch (e) { return '—'; }
}

function drawCards(list, offSite) {
  const box = document.getElementById('cards');
  box.innerHTML = '';
  list.forEach((page) => {
    const card = document.createElement('article');
    card.className = 'chat-card';
    const src = offSite ? localCopy(page.image) : page.image;
    card.innerHTML =
      '<div class="chat-image"><img alt="" loading="lazy"></div>' +
      '<div class="chat-text">' +
      '<div class="chat-site"></div>' +
      '<div class="chat-title"></div>' +
      '<div class="chat-desc"></div>' +
      '<div class="chat-host"></div>' +
      '</div>';
    card.querySelector('img').src = src;
    card.querySelector('.chat-site').textContent = page.siteName;
    card.querySelector('.chat-title').textContent = page.title;
    card.querySelector('.chat-desc').textContent = page.description;
    card.querySelector('.chat-host').textContent = host(page.canonical);
    box.appendChild(card);
  });
}

function loads(url) {
  return new Promise((resolve) => {
    const probe = new Image();
    probe.onload = () => resolve(true);
    probe.onerror = () => resolve(false);
    probe.src = url;
  });
}

async function everyDeclaredFileExists(list) {
  const missing = [];
  for (const page of list) {
    for (const href of page.declared) {
      const response = await fetch(href, { method: 'GET', cache: 'no-store' });
      if (!response.ok) { missing.push(page.file + ' → ' + href); }
    }
  }
  return missing;
}

function channel(value) {
  const c = value / 255;
  return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
}

function luminance(hex) {
  const h = hex.trim().replace('#', '');
  const parts = [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
  return 0.2126 * channel(parts[0]) + 0.7152 * channel(parts[1]) + 0.0722 * channel(parts[2]);
}

function contrast(a, b) {
  const la = luminance(a), lb = luminance(b);
  return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
}

function row(ok, text) {
  const li = document.createElement('li');
  li.className = ok ? 'ok' : 'bad';
  li.textContent = (ok ? '✓ ' : '✗ ') + text;
  return li;
}

function unique(values) {
  return new Set(values.filter(Boolean)).size === values.filter(Boolean).length;
}

async function drawChecks(list) {
  const box = document.getElementById('checks');
  box.innerHTML = '';

  const absolute = list.every((p) => /^https:\/\//.test(p.image));
  const reachable = absolute ? (await Promise.all(list.map((p) => loads(p.image)))).every(Boolean) : false;
  box.appendChild(row(absolute && reachable,
    'Адрес картинки превью абсолютный и картинка по нему открывается'));

  const missing = await everyDeclaredFileExists(list);
  box.appendChild(row(missing.length === 0,
    missing.length === 0
      ? 'Каждый объявленный в шапке файл существует'
      : 'Объявлено, но не найдено: ' + missing.join(', ')));

  box.appendChild(row(list.every((p) => p.siteName && p.title &&
    p.siteName.toLowerCase() !== p.title.toLowerCase()),
    'Название сайта не повторяет заголовок страницы'));

  box.appendChild(row(
    unique(list.map((p) => p.title)) &&
    unique(list.map((p) => p.description)) &&
    unique(list.map((p) => p.image)) &&
    unique(list.map((p) => p.canonical)),
    'У каждой страницы свои заголовок, описание, картинка и canonical'));

  const style = getComputedStyle(document.documentElement);
  const field = style.getPropertyValue('--field');
  const arrow = style.getPropertyValue('--arrow');
  const ratio = contrast(field, arrow);
  box.appendChild(row(ratio >= 4.5,
    'Контраст пары цветов знака ' + ratio.toFixed(2) + ':1 при пороге 4.5:1'));
}

function drawSheets() {
  ['sheet-light', 'sheet-dark'].forEach((id) => {
    const box = document.getElementById(id);
    box.innerHTML = '';
    ICON_SIZES.forEach((size) => {
      const wrap = document.createElement('figure');
      const img = document.createElement('img');
      img.src = 'icons/icon-' + size + '.png';
      img.width = size;
      img.height = size;
      img.alt = 'Значок ' + size + ' пикселей';
      const caption = document.createElement('figcaption');
      caption.textContent = size + ' px';
      wrap.appendChild(img);
      wrap.appendChild(caption);
      box.appendChild(wrap);
    });
  });
}

(async function () {
  drawSheets();
  try {
    const list = [];
    for (const file of FILES) { list.push(await readPage(file)); }
    const offSite = list.some((p) => p.image && !sameOrigin(p.image));
    if (offSite) {
      const warn = document.getElementById('warning');
      warn.hidden = false;
      warn.textContent = 'Сайт открыт не по рабочему адресу, поэтому в карточках' +
        ' показаны местные копии картинок. Проверка ниже всё равно идёт по тем' +
        ' абсолютным адресам, что стоят в шапках страниц.';
    }
    drawCards(list, offSite);
    await drawChecks(list);
  } catch (error) {
    document.getElementById('cards').textContent =
      'Не удалось прочитать страницы: ' + error.message +
      '. Витрина работает только по адресу http://, а не при открытии файла с диска.';
  }
})();
</script>
</body>
</html>
```

- [ ] **Шаг 2: Дописать стили витрины в конец `styles.css`**

```css
/* --- витрина --- */

.section { margin: 36px 0 6px; font-size: 24px; color: var(--field); }

.warn {
  margin: 0 0 18px;
  padding: 11px 14px;
  border-radius: 10px;
  background: #fff5d6;
  border: 1px solid #efd98a;
  color: #6a5312;
  font-size: 15px;
}

.cards-row {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}

.chat-card {
  border: 1px solid var(--line);
  border-radius: 14px;
  overflow: hidden;
  background: var(--paper);
  border-left: 4px solid var(--field);
}
.chat-image { aspect-ratio: 1200 / 630; background: var(--shade); }
.chat-image img { display: block; width: 100%; height: 100%; object-fit: cover; }
.chat-text { padding: 12px 14px 14px; }
.chat-site { font-weight: 700; font-size: 14px; color: var(--field); }
.chat-title { font-weight: 700; margin-top: 3px; }
.chat-desc { color: var(--muted); font-size: 15px; margin-top: 4px; }
.chat-host { color: #8a9ab5; font-size: 13px; margin-top: 8px; }

.checks { list-style: none; padding: 0; margin: 10px 0 0; }
.checks li {
  padding: 9px 12px;
  border-radius: 9px;
  margin-bottom: 7px;
  font-size: 15px;
}
.checks li.ok { background: #eaf6ee; color: #17603a; }
.checks li.bad { background: #fdecec; color: #8d2020; }

.sheet {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 22px;
  padding: 18px;
  border-radius: 12px;
  margin-bottom: 10px;
  overflow-x: auto;
}
.sheet.light { background: #ffffff; border: 1px solid var(--line); }
.sheet.dark { background: #1E1E1E; }
.sheet figure { margin: 0; text-align: center; }
.sheet img { display: block; margin: 0 auto 6px; image-rendering: auto; }
.sheet figcaption { font-size: 12px; color: var(--muted); }
.sheet.dark figcaption { color: #9aa7bd; }
.sheet img[width="512"] { width: 180px; height: 180px; }
```

Последняя строка нужна, чтобы картинка 512 не растягивала страницу: файл остаётся настоящим, показывается уменьшённым.

- [ ] **Шаг 3: Добавить в `tools/check.py` проверку витрины и сверку цветов**

Вставить рядом с `ICON_RELS`:

```python
EXTRA_PAGES = ("showcase.html",)
```

Добавить функцию перед `main`:

```python
def _check_colours(root):
    """Цвета знака живут в mark.py, а витрина считает контраст по переменным
    из styles.css. Если они разойдутся, витрина покажет неправду."""
    path = root / "styles.css"
    if not path.exists():
        return ["styles.css: файла нет"]
    text = path.read_text(encoding="utf-8")
    problems = []
    for name, expected in (("--field", mark.FIELD), ("--arrow", mark.ARROW)):
        needle = "%s: %s;" % (name, expected)
        if needle not in text:
            problems.append("styles.css: переменная %s разошлась с mark.py "
                            "(ожидается %s)" % (name, expected))
    return problems


def _check_extra_pages(root):
    problems = []
    for name in EXTRA_PAGES:
        path = root / name
        if not path.exists():
            continue
        head = parse_head(path.read_text(encoding="utf-8"))
        if "noindex" not in (meta_value(head, "robots") or ""):
            problems.append("%s: нет noindex" % name)
        for href, sizes in _declared_files(head):
            if not (root / href).exists():
                problems.append("%s: в шапке объявлен %s, а по этому адресу "
                                "ничего нет" % (name, href))
            else:
                _check_png_side(root, href, sizes, name, problems.append)
    return problems
```

В конце `check_files`, перед `return problems`, дописать две строки к трём уже стоящим — получится так:

```python
    problems.extend(_check_manifest(root))
    problems.extend(_check_robots(root))
    problems.extend(_check_icon_names(root))
    problems.extend(_check_colours(root))
    problems.extend(_check_extra_pages(root))
    return problems
```

В `copy_site` внутри `tests/test_check.py` добавить `"styles.css"` — он там уже есть в списке, проверить, что не потерялся.

- [ ] **Шаг 4: Дописать два теста в `tests/test_check.py`**

```python
class TestShowcase(CheckCase):
    def test_витрина_тоже_закрыта_от_поисковиков(self):
        p = self.tmp / "showcase.html"
        text = p.read_text(encoding="utf-8")
        p.write_text(text.replace('content="noindex, nofollow"', 'content="all"'),
                     encoding="utf-8")
        self.assertComplains("showcase.html: нет noindex")

    def test_цвета_в_css_не_должны_расходиться_с_mark(self):
        p = self.tmp / "styles.css"
        text = p.read_text(encoding="utf-8")
        p.write_text(text.replace("--field: #0A2A66;", "--field: #123456;"),
                     encoding="utf-8")
        self.assertComplains("--field")
```

- [ ] **Шаг 5: Запустить тесты и проверку**

```bash
cd ~/Progects/dostavka-ikonki && python3 -m unittest discover -s tests -v && python3 -m tools.check
```

Ожидается: все тесты OK, проверка без замечаний.

- [ ] **Шаг 6: Коммит**

```bash
cd ~/Progects/dostavka-ikonki && git add showcase.html styles.css tools/check.py tests/test_check.py && git commit -m "Витрина: карточки собираются из живых тегов страниц, ни один заголовок не написан руками

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Задача 9: Инструкция владельцу сайта и обновлённый README

**Файлы:**
- Создать: `docs/УСТАНОВКА.md`
- Изменить: `README.md`

**Интерфейсы:** ничего программного.

- [ ] **Шаг 1: Написать `docs/УСТАНОВКА.md`**

Инструкция для человека, который получит комплект и будет ставить его на свой сайт. Писать простыми словами, без жаргона.

Обязательные разделы, каждый с настоящим содержимым, а не с заголовком:

1. **Что лежит в комплекте** — перечислить файлы и сказать, зачем каждый.
2. **Куда положить файлы** — папка `icons/` рядом с главной страницей, `site.webmanifest` — в корень.
3. **Что вставить в шапку каждой страницы** — готовый кусок HTML с пояснением,
   что `og:image`, `og:url` и `canonical` у каждой страницы свои и адрес пишется
   полностью, с `https://` и доменом.
4. **Как проверить, что всё встало** — открыть сайт, посмотреть вкладку, затем
   прогнать `python3 -m tools.check --live https://адрес-сайта/`.
5. **Кэш мессенджеров** — главный раздел, ради которого инструкцию и пишут:

   > Мессенджер запоминает карточку при первой пересылке ссылки. Поменяли теги —
   > в чате ещё долго будет старое превью, и это не ошибка установки.
   > Telegram: отправить адрес боту @WebpageBot, он сбросит запомненное.
   > ВКонтакте: страница отладчика Open Graph на vk.com.
   > WhatsApp: сброса нет. Помогает только новый адрес страницы.

6. **Чего комплект не делает** — не обещает одинаковый вид карточки во всех
   мессенджерах (правила у них разные и меняются), не даёт офлайнового режима
   и установки приложением.

- [ ] **Шаг 2: Обновить `README.md`**

Заменить раздел «Состояние на 21.09.2026» на настоящее состояние и добавить раздел «Как собрать и проверить»:

```markdown
## Как собрать и проверить

Нужен только системный Python 3 — ни npm, ни установки пакетов.

Собрать весь комплект заново:

    python3 -m tools.build

Прогнать проверки по файлам:

    python3 -m tools.check

Прогнать проверки по живому адресу:

    python3 -m tools.check --live https://pyhphhddb8-eng.github.io/dostavka-ikonki/

Запустить тесты:

    python3 -m unittest discover -s tests

Посмотреть сайт у себя:

    python3 -m http.server 8000

и открыть http://localhost:8000/showcase.html — витрина работает только
по адресу http://, при открытии файла с диска браузер не даст ей прочитать
соседние страницы.

Новая страница сайта — это новая строка в `content/pages.tsv` и новый
HTML-файл с метками `head:begin` и `head:end` в шапке. Всё остальное
сделает `python3 -m tools.build`.
```

- [ ] **Шаг 3: Коммит**

```bash
cd ~/Progects/dostavka-ikonki && git add README.md docs/УСТАНОВКА.md && git commit -m "Инструкция по установке комплекта на чужой сайт и порядок сборки в README

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---
## Задача 10: Предпросмотр в браузере и проверки, которые скриптом не сделать

Часть заявленного проверяется только в живом браузере: что витрина показывает ровно те заголовки, что стоят в шапках страниц; что на узком экране нет горизонтальной прокрутки; что консоль чистая; что значок действительно появляется во вкладке.

**Файлы:** ничего не создаётся. Правки — по результатам.

- [ ] **Шаг 1: Поднять сайт у себя**

```bash
cd ~/Progects/dostavka-ikonki && python3 -m http.server 8000
```

Оставить работать в отдельной вкладке терминала. Дальше всё открывается по адресу `http://localhost:8000/`.

- [ ] **Шаг 2: Открыть витрину и снять скриншот**

Через Playwright: перейти на `http://localhost:8000/showcase.html`, дождаться появления карточек, снять скриншот всей страницы.

Смотреть на снимке: три разные картинки, три разных заголовка, все пять строк проверки зелёные, контактный лист значка читается и на светлом, и на тёмном.

- [ ] **Шаг 3: Сверить витрину с живыми тегами текстом, а не взглядом**

Выполнить в странице витрины:

```js
(async () => {
  const files = ['index.html', 'track.html', 'promo.html'];
  const fromPages = [];
  for (const f of files) {
    const doc = new DOMParser().parseFromString(await (await fetch(f)).text(), 'text/html');
    fromPages.push(doc.querySelector('meta[property="og:title"]').content);
  }
  const onScreen = [...document.querySelectorAll('.chat-title')].map((n) => n.textContent);
  return { fromPages, onScreen, equal: JSON.stringify(fromPages) === JSON.stringify(onScreen) };
})()
```

Ожидается: `equal: true`. Если `false` — витрина расходится с тегами, и это разбирать до всего остального.

- [ ] **Шаг 4: Проверить узкий экран**

Выставить окно 360 пикселей по ширине и на каждой из четырёх страниц выполнить:

```js
({ scrollWidth: document.documentElement.scrollWidth,
   clientWidth: document.documentElement.clientWidth,
   overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth })
```

Ожидается: `overflow: false` на всех четырёх. Чаще всего вылезает контактный лист значка — у него `overflow-x: auto`, и прокручиваться должен он сам, а не страница.

- [ ] **Шаг 5: Проверить консоль**

Прочитать сообщения консоли на всех четырёх страницах. Ожидается: пусто. Любая ошибка 404 здесь — это объявленный, но не положенный файл, то есть ровно та ошибка, которую работа обещает не допускать.

- [ ] **Шаг 6: Убедиться, что значок появился во вкладке**

Открыть `http://localhost:8000/` в обычном браузере и посмотреть на вкладку глазами. На скриншоте Playwright вкладки не видно, поэтому этот шаг делается руками.

- [ ] **Шаг 7: Снять скриншоты всех четырёх страниц на 360 и на 1280 пикселей**

Понадобятся, чтобы показать работу и сравнить, если что-то поедет позже.

- [ ] **Шаг 8: Внести правки и перепроверить**

Любая правка вёрстки → заново шаги 3–5. Любая правка текстов → сначала `python3 -m tools.build`, потом заново.

- [ ] **Шаг 9: Коммит**

```bash
cd ~/Progects/dostavka-ikonki && git add -A && git commit -m "Правки по предпросмотру: узкий экран, чистая консоль, сверка витрины с тегами

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Задача 11: Выкладка на GitHub Pages и проверка на живом адресе

**Файлы:** ничего не создаётся.

- [ ] **Шаг 1: Убедиться, что всё собрано и проверено**

```bash
cd ~/Progects/dostavka-ikonki && python3 -m tools.build && python3 -m tools.check && python3 -m unittest discover -s tests && git status --short
```

Ожидается: сборка проходит, замечаний нет, тесты OK, `git status` пустой.

- [ ] **Шаг 2: Проверить, под каким аккаунтом работает gh**

```bash
gh auth status
```

Ожидается: `pyhphhddb8-eng`. Если аккаунт другой — остановиться и спросить, а не выкладывать под чужим.

- [ ] **Шаг 3: Создать репозиторий и залить**

```bash
cd ~/Progects/dostavka-ikonki && gh repo create pyhphhddb8-eng/dostavka-ikonki --public --source=. --remote=origin --push --description "Значок сайта и превью ссылок для службы доставки: комплект значков, своё превью у каждой страницы, витрина из живых тегов"
```

- [ ] **Шаг 4: Включить GitHub Pages из корня ветки main**

```bash
gh api -X POST repos/pyhphhddb8-eng/dostavka-ikonki/pages -f "source[branch]=main" -f "source[path]=/"
```

Если ответ говорит, что Pages уже включены, это не ошибка — идти дальше.

- [ ] **Шаг 5: Дождаться выкладки**

```bash
cd ~/Progects/dostavka-ikonki && until curl -sS -o /dev/null -w "%{http_code}" https://pyhphhddb8-eng.github.io/dostavka-ikonki/ | grep -q 200; do sleep 15; echo "жду…"; done; echo "сайт поднялся"
```

Первая выкладка обычно занимает минуту-две.

- [ ] **Шаг 6: Прогнать проверки по живому адресу**

Это главный шаг задачи: на диске файл может лежать, а Pages его не раздавать.

```bash
cd ~/Progects/dostavka-ikonki && python3 -m tools.check --live https://pyhphhddb8-eng.github.io/dostavka-ikonki/
```

Ожидается: `Проверки пройдены, замечаний нет.`

- [ ] **Шаг 7: Убедиться, что robots.txt на живом адресе не закрывает сайт**

```bash
curl -sS https://pyhphhddb8-eng.github.io/dostavka-ikonki/robots.txt
```

Ожидается: комментарий и `Allow: /`. Глухого `Disallow: /` быть не должно — иначе бот мессенджера не соберёт карточку, и работа про превью останется без превью.

Отдельно проверить, что GitHub не подставил свой общий `robots.txt`: адрес выше должен отдавать именно наш файл.

- [ ] **Шаг 8: Открыть витрину на живом адресе**

`https://pyhphhddb8-eng.github.io/dostavka-ikonki/showcase.html`

На живом адресе жёлтая полоса-предупреждение про местные копии картинок появляться не должна: адреса совпали с рабочими. Все пять строк проверки — зелёные.

- [ ] **Шаг 9: Переслать ссылку в Telegram и посмотреть на карточку**

Переслать себе три ссылки подряд: главную, `track.html` и `promo.html`. Убедиться, что карточки разные. Если у какой-то карточки нет картинки — сбросить кэш через @WebpageBot и переслать снова.

Это единственная настоящая проверка результата. Скриншот переписки в работу не кладётся — витрина честно называет себя макетом, и подменять её снимком нельзя.

- [ ] **Шаг 10: Записать в журнал**

Обновить `~/Obsidian/Brain/index.md`: что сделано, что дальше, дата. Решения, которые стоит помнить — выбор GitHub Pages для демонстрационной работы, отказ от глухого `Disallow` в `robots.txt`, отказ от онлайновых генераторов фавиконов — записать в `~/Obsidian/Brain/decisions.md`.

- [ ] **Шаг 11: Последний коммит и отправка**

```bash
cd ~/Progects/dostavka-ikonki && git add -A && git commit -m "Работа выложена и проверена на живом адресе

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>" && git push
```

---

## Проверка плана по спеке

Пройдено по каждому разделу спеки, чтобы не осталось необеспеченных обещаний.

| Обещание спеки | Где делается |
|---|---|
| Три страницы, каждая попадает в чат отдельной ссылкой | Задача 5 |
| Страница не собирает никаких данных | Задача 5, шаги 4–6; поле на `track.html` только показывает заранее заданное |
| Отслеживание ненастоящее и об этом сказано | Задача 5, шаг 5 |
| Значок 16, 32, 48, 180, 192, 512 | Задача 2 |
| `favicon.ico` и `favicon.svg` | Задача 2 |
| Значок для iPhone и `site.webmanifest` | Задачи 2 и 6 |
| Манифест только ради значка, без обещаний приложения | Задача 6, `display: browser` |
| Превью 1200×630 своё у каждой страницы | Задача 4 |
| Витрина | Задача 8 |
| Инструкция по установке на чужой сайт | Задача 9 |
| Скруглённый квадрат и широкая стрелка, две фигуры | Задача 1 |
| Контраст проверяется по формуле | Задача 1, `test_arrow_reads_on_field` |
| Знак рисуется кодом из одного исходника | Задача 1, `tools/mark.py` |
| Ошибка 1: относительный адрес картинки превью | Задача 7, `test_относительный_адрес_картинки_превью` |
| Ошибка 2: объявленного файла нет | Задача 7, `test_объявленного_файла_нет` |
| Ошибка 3: название сайта повторяет заголовок | Задача 7, `test_название_сайта_повторяет_заголовок` |
| Ошибка 4: одна картинка на весь сайт | Задача 7, `test_одна_картинка_на_весь_сайт` |
| Ошибка 5: значок читается только крупно | Задача 1 (`test_stroke_thick_enough_at_16px`) и контактный лист в задаче 8 |
| Обычные HTML-страницы, без зависимостей и без npm | Глобальные ограничения, задача 5 |
| Тексты превью в одном файле, строка на страницу | Задача 3, `content/pages.tsv` |
| Скрипт собирает картинки и подставляет теги | Задачи 4 и 5 |
| Витрина строится из живых тегов | Задача 8 |
| Шрифт подрезан и вшит | Задача 3 |
| Про кэш мессенджеров сказано в инструкции | Задача 9, раздел 5 |
| `noindex` мета-тегом, а не запретом в `robots.txt` | Задача 6, проверяется в задачах 7 и 11 |
| Каждый объявленный файл отдаётся, сторона совпадает с именем и тегом | Задача 7, `_check_png_side` |
| Картинки 1200×630 и легче 300 КБ | Задачи 4 и 7 |
| Заголовки, описания и картинки попарно различны | Задачи 3 и 7 |
| У каждой страницы свой `canonical` | Задачи 5 и 7 |
| Манифест разбирается, значки существуют | Задача 7, `_check_manifest` |
| Витрина показывает те же заголовки — сверяется текстом | Задача 10, шаг 3 |
| На 360 пикселях нет горизонтальной прокрутки | Задача 10, шаг 4 |
| Консоль чистая | Задача 10, шаг 5 |
| Значок реально появляется во вкладке | Задача 10, шаг 6 |
| Выкладка на GitHub Pages, аккаунт `pyhphhddb8-eng` | Задача 11 |

Чего в работе сознательно нет: настоящего отслеживания, формы, приёма заявок, офлайнового режима, установки приложением и обещания одинакового вида карточки во всех мессенджерах. Ни одна задача этого не добавляет.

## Что может пойти не так

**Pillow не соберёт ICO из нескольких кадров.** Запасной путь описан прямо в задаче 2, шаг 4.

**Шрифт не скачается.** `tools/build_font.py` ходит в сеть только один раз; дальше полные TTF лежат в репозитории. Если сеть недоступна при первом запуске — взять PT Sans вручную со страницы `google/fonts`, папка `ofl/ptsans`, и положить в `tools/fonts_src/`.

**GitHub Pages отдаст свой `robots.txt` вместо нашего.** Проверяется в задаче 11, шаг 7. Наш файл лежит в корне сайта и должен перебивать общий.

**Телеграм покажет старую карточку.** Это кэш, а не ошибка. Сброс через @WebpageBot, об этом же написано в инструкции владельцу.
