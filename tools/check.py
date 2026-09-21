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
EXTRA_PAGES = ("showcase.html",)
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
    problems.extend(_check_colours(root))
    problems.extend(_check_extra_pages(root))
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


def _check_colours(root):
    """Цвета знака живут в mark.py, а витрина считает контраст по переменным
    из styles.css. Если они разойдутся, витрина покажет неправду."""
    path = root / "styles.css"
    if not path.exists():
        return ["styles.css: файла нет"]
    text = path.read_text(encoding="utf-8")
    problems = []
    for name, expected in (("--field", mark.FIELD), ("--arrow", mark.ARROW)):
        if "%s: %s;" % (name, expected) not in text:
            problems.append("styles.css: переменная %s разошлась с mark.py "
                            "(ожидается %s)" % (name, expected))
    return problems


def _check_extra_pages(root):
    """Витрина не описана в content/pages.tsv, но она такая же страница
    сайта, и объявленные в её шапке файлы обязаны существовать."""
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
