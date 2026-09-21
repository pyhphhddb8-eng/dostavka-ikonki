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
