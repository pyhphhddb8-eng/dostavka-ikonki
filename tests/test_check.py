import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image

from tools import check, pages


def copy_site(dest):
    """Копия готового сайта, на которой можно ломать что угодно."""
    for name in ("index.html", "track.html", "promo.html", "showcase.html",
                 "styles.css", "site.webmanifest", "robots.txt"):
        src = pages.ROOT / name
        if src.exists():
            shutil.copy2(src, dest / name)
    shutil.copytree(pages.ROOT / "icons", dest / "icons")
    shutil.copytree(pages.ROOT / "fonts", dest / "fonts")
    return dest


class CheckCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        copy_site(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def problems(self):
        return check.check_files(self.tmp)

    def assertComplains(self, needle):
        found = self.problems()
        self.assertTrue(
            any(needle in p for p in found),
            "проверка промолчала про %r, а нашла только: %s" % (needle, found),
        )


class TestCleanSite(CheckCase):
    def test_собранный_сайт_проходит_проверку(self):
        self.assertEqual(self.problems(), [])


class TestFiveMistakes(CheckCase):
    def test_относительный_адрес_картинки_превью(self):
        p = self.tmp / "index.html"
        text = p.read_text(encoding="utf-8")
        text = text.replace(
            'property="og:image" content="%s"' % pages.load()[0].og_image_url,
            'property="og:image" content="icons/og/index.png"',
        )
        p.write_text(text, encoding="utf-8")
        self.assertComplains("не абсолютный")

    def test_объявленного_файла_нет(self):
        (self.tmp / "icons" / "apple-touch-icon.png").unlink()
        self.assertComplains("apple-touch-icon.png")

    def test_название_сайта_повторяет_заголовок(self):
        p = self.tmp / "promo.html"
        text = p.read_text(encoding="utf-8")
        text = text.replace(
            'property="og:site_name" content="%s"' % pages.SITE_NAME,
            'property="og:site_name" content="Первая доставка за 1 рубль"',
        )
        p.write_text(text, encoding="utf-8")
        self.assertComplains("повторяет заголовок")

    def test_одна_картинка_на_весь_сайт(self):
        first = pages.load()[0].og_image_url
        p = self.tmp / "promo.html"
        text = p.read_text(encoding="utf-8")
        text = text.replace(pages.load()[2].og_image_url, first)
        p.write_text(text, encoding="utf-8")
        self.assertComplains("повторяется")

    def test_размер_файла_расходится_с_именем(self):
        path = self.tmp / "icons" / "icon-32.png"
        with Image.open(path) as img:
            img.resize((30, 30)).save(path)
        self.assertComplains("icon-32.png")


class TestOtherTraps(CheckCase):
    def test_глухой_запрет_в_robots(self):
        (self.tmp / "robots.txt").write_text(
            "User-agent: *\nDisallow: /\n", encoding="utf-8"
        )
        self.assertComplains("Disallow")

    def test_страница_не_закрыта_от_поисковиков(self):
        p = self.tmp / "track.html"
        text = p.read_text(encoding="utf-8")
        text = text.replace('content="noindex, nofollow"', 'content="all"')
        p.write_text(text, encoding="utf-8")
        self.assertComplains("noindex")

    def test_картинка_превью_слишком_тяжёлая(self):
        path = self.tmp / "icons" / "og" / "track.png"
        with open(path, "ab") as fh:
            fh.write(b"\0" * (310 * 1024))
        self.assertComplains("тяжелее")

    def test_манифест_обещает_несуществующий_значок(self):
        (self.tmp / "icons" / "icon-512.png").unlink()
        self.assertComplains("icon-512.png")


if __name__ == "__main__":
    unittest.main()
