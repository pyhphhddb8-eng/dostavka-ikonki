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
        for p in self.pages:
            with Image.open(self._path(p)) as img:
                self.assertEqual(img.size, (1200, 630), "%s: %s" % (p.slug, img.size))

    def test_light_enough_for_whatsapp(self):
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
