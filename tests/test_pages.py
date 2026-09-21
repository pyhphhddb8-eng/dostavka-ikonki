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
        for field in ("title", "description", "caption", "og_image_url", "url"):
            values = [getattr(p, field) for p in self.pages]
            for a, b in itertools.combinations(values, 2):
                self.assertNotEqual(a, b, "повтор в поле %s: %r" % (field, a))

    def test_site_name_does_not_repeat_the_title(self):
        for p in self.pages:
            self.assertNotEqual(p.title.strip().lower(), pages.SITE_NAME.strip().lower())

    def test_description_fits_the_card(self):
        for p in self.pages:
            self.assertLessEqual(len(p.description), 160, "%s: описание длиннее 160 знаков" % p.slug)
            self.assertGreaterEqual(len(p.description), 60, "%s: описание короче 60 знаков" % p.slug)

    def test_title_fits_the_card(self):
        for p in self.pages:
            self.assertLessEqual(len(p.title), 70, "%s: заголовок длиннее 70 знаков" % p.slug)

    def test_preview_addresses_are_absolute(self):
        for p in self.pages:
            self.assertTrue(p.og_image_url.startswith("https://"), p.og_image_url)
            self.assertTrue(p.url.startswith("https://"), p.url)

    def test_index_lives_at_the_root_address(self):
        index = self.pages[0]
        self.assertEqual(index.url, pages.BASE_URL)
        self.assertEqual(index.file_name, "index.html")
        self.assertEqual(self.pages[1].file_name, "track.html")


class TestFont(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Сборка обязана пройти до любой проверки этого класса: иначе на
        # чистой машине порядок тестов решает, упадут они или нет.
        from tools import build_font
        build_font.main()

    def test_subset_fonts_are_built_and_small(self):
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
