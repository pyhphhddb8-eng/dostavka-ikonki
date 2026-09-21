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
