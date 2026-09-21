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
