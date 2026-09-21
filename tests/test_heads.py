import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import build_heads, pages


class TestInject(unittest.TestCase):
    def test_replaces_only_between_the_marks(self):
        doc = "A\n%s\nстарое\n%s\nB" % (build_heads.BEGIN, build_heads.END)
        out = build_heads.inject(doc, "новое")
        self.assertIn("новое", out)
        self.assertNotIn("старое", out)
        self.assertTrue(out.startswith("A"))
        self.assertTrue(out.endswith("B"))
        self.assertIn(build_heads.BEGIN, out)
        self.assertIn(build_heads.END, out)

    def test_running_twice_changes_nothing(self):
        doc = "A\n%s\n\n%s\nB" % (build_heads.BEGIN, build_heads.END)
        once = build_heads.inject(doc, "новое")
        self.assertEqual(once, build_heads.inject(once, "новое"))

    def test_missing_marks_are_an_error_not_silence(self):
        with self.assertRaises(ValueError):
            build_heads.inject("<html></html>", "новое")


class TestHeadHtml(unittest.TestCase):
    def setUp(self):
        self.pages = pages.load()
        self.heads = {p.slug: build_heads.head_html(p) for p in self.pages}

    def test_preview_address_is_absolute(self):
        for slug, head in self.heads.items():
            found = re.findall(r'property="og:image" content="([^"]+)"', head)
            self.assertEqual(len(found), 1, slug)
            self.assertTrue(found[0].startswith("https://"), "%s: %s" % (slug, found[0]))

    def test_site_name_is_not_the_title(self):
        for slug, head in self.heads.items():
            title = re.search(r'property="og:title" content="([^"]+)"', head).group(1)
            name = re.search(r'property="og:site_name" content="([^"]+)"', head).group(1)
            self.assertNotEqual(title.lower(), name.lower(), slug)

    def test_every_page_has_its_own_canonical(self):
        canons = []
        for p in self.pages:
            found = re.search(r'rel="canonical" href="([^"]+)"', self.heads[p.slug])
            self.assertIsNotNone(found, p.slug)
            canons.append(found.group(1))
        self.assertEqual(len(set(canons)), len(canons))

    def test_closed_from_search_engines(self):
        for slug, head in self.heads.items():
            self.assertIn('name="robots" content="noindex, nofollow"', head, slug)

    def test_declares_the_whole_icon_set(self):
        for slug, head in self.heads.items():
            for needle in ('icons/favicon.svg', 'icons/favicon.ico',
                           'icons/apple-touch-icon.png', 'rel="manifest"',
                           'name="theme-color"'):
                self.assertIn(needle, head, "%s: нет %s" % (slug, needle))

    def test_card_size_is_declared(self):
        for slug, head in self.heads.items():
            self.assertIn('property="og:image:width" content="1200"', head, slug)
            self.assertIn('property="og:image:height" content="630"', head, slug)

    def test_no_external_requests(self):
        # canonical и og:image обязаны быть абсолютными, это не «наружу».
        # А вот загружаемое — стили, значки, манифест — должно лежать рядом,
        # иначе страница пойдёт в чужую сеть за файлом.
        for slug, head in self.heads.items():
            for line in head.splitlines():
                if "<link" not in line or 'rel="canonical"' in line:
                    continue
                found = re.search(r'href="([^"]+)"', line)
                self.assertIsNotNone(found, line)
                self.assertFalse(found.group(1).startswith("http"),
                                 "%s грузит файл со стороны: %s" % (slug, line.strip()))


class TestBuiltPages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build_heads.main()

    def test_each_file_got_its_own_head(self):
        for p in pages.load():
            text = (pages.ROOT / p.file_name).read_text(encoding="utf-8")
            self.assertIn(p.og_image_url, text, p.slug)
            self.assertIn(p.title, text, p.slug)


if __name__ == "__main__":
    unittest.main()
