import random
import unittest

from geom2d import convex_hull, polygon_orientation
from tests.brute import brute_hull_vertices


class TestConvexHull(unittest.TestCase):
    def test_square_with_interior(self):
        pts = [(0, 0), (4, 0), (4, 4), (0, 4), (2, 2), (1, 1)]
        self.assertEqual(convex_hull(pts),
                         [(0, 0), (4, 0), (4, 4), (0, 4)])

    def test_duplicates_removed(self):
        pts = [(0, 0), (1, 0), (1, 1), (0, 1)] * 5
        self.assertEqual(convex_hull(pts),
                         [(0, 0), (1, 0), (1, 1), (0, 1)])

    def test_fewer_than_three_unique(self):
        self.assertEqual(convex_hull([]), [])
        self.assertEqual(convex_hull([(3, 3)]), [(3, 3)])
        self.assertEqual(convex_hull([(2, 2), (2, 2), (2, 2)]), [(2, 2)])
        self.assertEqual(convex_hull([(2, 2), (0, 0), (2, 2)]),
                         [(0, 0), (2, 2)])

    def test_all_collinear(self):
        pts = [(i, i) for i in range(10)]
        self.assertEqual(convex_hull(pts), [(0, 0), (9, 9)])
        full = convex_hull(pts, include_collinear=True)
        # Boundary is traced out and back: 2 * 10 - 2 vertices.
        self.assertEqual(len(full), 18)
        self.assertEqual(full[0], (0, 0))
        self.assertIn((9, 9), full)

    def test_collinear_edges_dropped_by_default(self):
        pts = [(0, 0), (2, 0), (4, 0), (4, 4), (0, 4)]
        self.assertEqual(convex_hull(pts), [(0, 0), (4, 0), (4, 4), (0, 4)])
        kept = convex_hull(pts, include_collinear=True)
        self.assertIn((2, 0), kept)

    def test_ccw_and_canonical_start(self):
        rng = random.Random(5)
        for _ in range(50):
            pts = [(rng.randint(-30, 30), rng.randint(-30, 30))
                   for _ in range(20)]
            hull = convex_hull(pts)
            if len(hull) >= 3:
                self.assertEqual(polygon_orientation(hull), "ccw")
                self.assertEqual(hull[0], min(hull))
            # Determinism.
            self.assertEqual(hull, convex_hull(list(reversed(pts))))

    def test_random_vs_brute(self):
        rng = random.Random(2024)
        for _ in range(150):
            pts = [(rng.randint(-8, 8), rng.randint(-8, 8))
                   for _ in range(rng.randint(3, 12))]
            hull = convex_hull(pts)
            self.assertEqual(set(hull), brute_hull_vertices(pts))


if __name__ == "__main__":
    unittest.main()
