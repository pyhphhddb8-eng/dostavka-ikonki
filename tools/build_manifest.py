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
