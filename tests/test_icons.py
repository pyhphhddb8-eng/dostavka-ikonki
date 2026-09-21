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
        path = ICONS / "apple-touch-icon.png"
        with Image.open(path) as img:
            self.assertEqual(img.size, (180, 180))
            self.assertEqual(img.mode, "RGB")
            corner = img.getpixel((0, 0))
        expected = tuple(int(mark.FIELD.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
        self.assertEqual(corner, expected)

    def test_svg_is_vector_and_parses(self):
        import xml.etree.ElementTree as ET
        root = ET.parse(ICONS / "favicon.svg").getroot()
        self.assertTrue(root.tag.endswith("svg"))

    def test_nothing_is_heavy(self):
        for path in ICONS.glob("icon-*.png"):
            self.assertLess(path.stat().st_size, 40 * 1024, "%s слишком тяжёлый" % path.name)


if __name__ == "__main__":
    unittest.main()
