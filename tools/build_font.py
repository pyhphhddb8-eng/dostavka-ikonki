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
