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
