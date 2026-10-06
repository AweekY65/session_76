import random
import unittest

from geom2d import (area, signed_area2, polygon_orientation,
                    classify_point, point_in_polygon)
from tests.brute import exact_point_in_polygon, star_polygon

SQUARE = [(0, 0), (4, 0), (4, 4), (0, 4)]
# Concave "arrow" polygon.
CONCAVE = [(0, 0), (4, 0), (4, 4), (2, 2), (0, 4)]


class TestAreaOrientation(unittest.TestCase):
    def test_area(self):
        self.assertEqual(area(SQUARE), 16)
        self.assertEqual(area(list(reversed(SQUARE))), 16)
        self.assertEqual(signed_area2(SQUARE), 32)
        self.assertEqual(signed_area2(list(reversed(SQUARE))), -32)

    def test_orientation(self):
        self.assertEqual(polygon_orientation(SQUARE), "ccw")
        self.assertEqual(polygon_orientation(list(reversed(SQUARE))), "cw")

    def test_degenerate(self):
        self.assertEqual(area([]), 0)
        self.assertEqual(area([(1, 1)]), 0)
        self.assertEqual(area([(0, 0), (2, 2)]), 0)
        self.assertEqual(area([(0, 0), (1, 1), (2, 2), (3, 3)]), 0)
        self.assertEqual(polygon_orientation([(0, 0), (1, 1), (2, 2)]),
                         "degenerate")
        self.assertEqual(polygon_orientation([]), "degenerate")

    def test_concave_area(self):
        self.assertEqual(area(CONCAVE), 12)


class TestClassifyPoint(unittest.TestCase):
    def test_convex(self):
        self.assertEqual(classify_point(SQUARE, (2, 2)), "inside")
        self.assertEqual(classify_point(SQUARE, (5, 2)), "outside")
        self.assertEqual(classify_point(SQUARE, (0, 2)), "boundary")
        self.assertEqual(classify_point(SQUARE, (4, 4)), "boundary")

    def test_concave(self):
        # (2, 3) sits in the notch cut out of the 4x4 square.
        self.assertEqual(classify_point(CONCAVE, (2, 3)), "outside")
        self.assertEqual(classify_point(CONCAVE, (1, 1)), "inside")
        self.assertEqual(classify_point(CONCAVE, (3, 1)), "inside")
        self.assertEqual(classify_point(CONCAVE, (2, 2)), "boundary")  # vertex
        self.assertEqual(classify_point(CONCAVE, (2, 0)), "boundary")  # edge

    def test_include_boundary_flag(self):
        self.assertTrue(point_in_polygon(SQUARE, (0, 2)))
        self.assertFalse(point_in_polygon(SQUARE, (0, 2),
                                          include_boundary=False))

    def test_degenerate_polygons(self):
        self.assertEqual(classify_point([], (0, 0)), "outside")
        self.assertEqual(classify_point([(1, 1)], (1, 1)), "boundary")
        self.assertEqual(classify_point([(1, 1)], (0, 0)), "outside")
        self.assertEqual(classify_point([(0, 0), (2, 0)], (1, 0)), "boundary")
        self.assertEqual(classify_point([(0, 0), (2, 0)], (1, 1)), "outside")

    def test_random_vs_exact(self):
        rng = random.Random(99)
        tested = 0
        while tested < 300:
            pts = list({(rng.randint(-10, 10), rng.randint(-10, 10))
                        for _ in range(8)})
            if len(pts) < 3:
                continue
            poly = star_polygon(pts)
            q = (rng.randint(-12, 12), rng.randint(-12, 12))
            expected = exact_point_in_polygon(poly, q)
            got = classify_point(poly, q)
            self.assertEqual(got, expected, (poly, q))
            tested += 1


if __name__ == "__main__":
    unittest.main()
