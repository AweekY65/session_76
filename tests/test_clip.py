import random
import unittest

from geom2d import (clip_convex, convex_hull, area, polygon_orientation,
                    point_in_polygon, classify_point)

SQUARE = [(0, 0), (4, 0), (4, 4), (0, 4)]


class TestClipConvex(unittest.TestCase):
    def test_half_clip(self):
        tri = [(2, -1), (2, 5), (6, 2)]  # right half sticks out of square
        out = clip_convex(tri, SQUARE)
        self.assertAlmostEqual(area(out), 23.0 / 3.0)
        for v in out:
            self.assertTrue(point_in_polygon(SQUARE, v))

    def test_subject_inside(self):
        small = [(1, 1), (2, 1), (2, 2), (1, 2)]
        self.assertEqual(clip_convex(small, SQUARE), small)

    def test_clip_inside_subject(self):
        big = [(-1, -1), (5, -1), (5, 5), (-1, 5)]
        out = clip_convex(big, SQUARE)
        self.assertAlmostEqual(area(out), area(SQUARE))
        self.assertEqual(len(out), 4)

    def test_disjoint(self):
        far = [(10, 10), (12, 10), (11, 12)]
        self.assertEqual(clip_convex(far, SQUARE), [])

    def test_edge_touch(self):
        tri = [(4, 0), (8, 0), (4, 4)]  # shares the x=4 edge with square
        out = clip_convex(tri, SQUARE)
        self.assertEqual(area(out), 0.0)

    def test_stable_order_and_determinism(self):
        subj = [(1, -1), (5, 1), (3, 6), (-2, 2)]
        clip = [(0, 0), (4, 0), (4, 4), (0, 4)]
        out1 = clip_convex(subj, clip)
        out2 = clip_convex(subj, clip)
        self.assertEqual(out1, out2)
        # Vertices follow subject traversal order -> same winding as subject.
        if len(out1) >= 3:
            self.assertEqual(polygon_orientation(out1),
                             polygon_orientation(subj))

    def test_degenerate_inputs(self):
        self.assertEqual(clip_convex([], SQUARE), [])
        self.assertEqual(clip_convex(SQUARE, []), [])
        self.assertEqual(clip_convex([(0, 0), (1, 1)], SQUARE), [])

    def test_random_cross_validation(self):
        # Sampled membership test: a point is inside the clipped polygon iff
        # it is inside both input polygons.
        rng = random.Random(31337)
        for _ in range(60):
            subj = convex_hull([(rng.uniform(-6, 6), rng.uniform(-6, 6))
                                for _ in range(rng.randint(3, 10))])
            clip = convex_hull([(rng.uniform(-6, 6), rng.uniform(-6, 6))
                                for _ in range(rng.randint(3, 10))])
            if len(subj) < 3 or len(clip) < 3:
                continue
            out = clip_convex(subj, clip)
            if len(out) < 3:
                continue
            self.assertLessEqual(area(out),
                                 min(area(subj), area(clip)) + 1e-6)
            for _ in range(30):
                q = (rng.uniform(-6, 6), rng.uniform(-6, 6))
                in_out = classify_point(out, q)
                in_both = (point_in_polygon(subj, q)
                           and point_in_polygon(clip, q))
                if in_out == "boundary":
                    continue  # boundary sampling is not stable to compare
                self.assertEqual(in_out == "inside", in_both,
                                 (subj, clip, out, q))


if __name__ == "__main__":
    unittest.main()
