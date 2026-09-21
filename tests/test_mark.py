import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import mark


class TestContrast(unittest.TestCase):
    def test_arrow_reads_on_field(self):
        # Стрелка на поле знака: пара должна проходить порог 4.5:1.
        self.assertGreaterEqual(mark.contrast(mark.FIELD, mark.ARROW), 4.5)

    def test_field_reads_on_light_tab(self):
        # На светлой вкладке знак виден силуэтом синего поля.
        self.assertGreaterEqual(mark.contrast(mark.FIELD, "#FFFFFF"), 3.0)

    def test_arrow_reads_on_dark_tab(self):
        # На тёмной вкладке синее поле почти сливается с фоном,
        # и читаемость держит жёлтая стрелка.
        self.assertGreaterEqual(mark.contrast(mark.ARROW, "#1E1E1E"), 3.0)

    def test_known_value(self):
        self.assertAlmostEqual(mark.contrast("#000000", "#FFFFFF"), 21.0, places=1)


class TestArrowGeometry(unittest.TestCase):
    def test_seven_points(self):
        self.assertEqual(len(mark.arrow_points(100)), 7)

    def test_fits_inside_square(self):
        pts = mark.arrow_points(100)
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        self.assertGreater(min(xs), 10)
        self.assertLess(max(xs), 90)
        self.assertGreater(min(ys), 10)
        self.assertLess(max(ys), 90)

    def test_centred(self):
        pts = mark.arrow_points(100)
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        self.assertAlmostEqual((min(xs) + max(xs)) / 2, 50.0, places=3)
        self.assertAlmostEqual((min(ys) + max(ys)) / 2, 50.0, places=3)

    def test_points_up_and_right(self):
        # Остриё стрелки — самая правая точка, и она выше середины.
        pts = mark.arrow_points(100)
        tip = max(pts, key=lambda p: p[0])
        self.assertLess(tip[1], 50.0)

    def test_scales_linearly(self):
        small = mark.arrow_points(100)
        big = mark.arrow_points(400)
        for (sx, sy), (bx, by) in zip(small, big):
            self.assertAlmostEqual(bx, sx * 4, places=6)
            self.assertAlmostEqual(by, sy * 4, places=6)

    def test_stroke_thick_enough_at_16px(self):
        # Настоящий размер значка во вкладке — 16 пикселей.
        pts = mark.arrow_points(16)
        ys = [p[1] for p in pts]
        xs = [p[0] for p in pts]
        diag = ((max(xs) - min(xs)) ** 2 + (max(ys) - min(ys)) ** 2) ** 0.5
        self.assertGreater(diag, 12.0)


class TestRendering(unittest.TestCase):
    def test_svg_has_one_rect_and_one_polygon(self):
        out = mark.svg(512)
        self.assertEqual(out.count("<rect"), 1)
        self.assertEqual(out.count("<polygon"), 1)
        self.assertIn(mark.FIELD, out)
        self.assertIn(mark.ARROW, out)
        self.assertIn('viewBox="0 0 512 512"', out)

    def test_png_size_and_colours(self):
        img = mark.png(64)
        self.assertEqual(img.size, (64, 64))
        self.assertEqual(img.mode, "RGBA")
        r, g, b, a = img.getpixel((32, 32))
        self.assertEqual(a, 255)
        self.assertGreater(r, 200)
        self.assertGreater(g, 150)
        self.assertLess(b, 100)

    def test_png_corner_is_transparent(self):
        img = mark.png(64)
        self.assertLess(img.getpixel((0, 0))[3], 40)


if __name__ == "__main__":
    unittest.main()
