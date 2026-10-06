import random
import unittest

from geom2d import segments_intersect, segment_intersection
from tests.brute import exact_segments_intersect


class TestSegmentsIntersect(unittest.TestCase):
    def test_proper_cross(self):
        self.assertTrue(segments_intersect((0, 0), (2, 2), (0, 2), (2, 0)))
        self.assertFalse(segments_intersect((0, 0), (1, 1), (0, 2), (1, 3)))

    def test_endpoint_touch(self):
        self.assertTrue(segments_intersect((0, 0), (1, 1), (1, 1), (2, 0)))
        self.assertTrue(segments_intersect((0, 0), (2, 0), (2, 0), (2, 2)))

    def test_collinear(self):
        self.assertTrue(segments_intersect((0, 0), (3, 0), (1, 0), (2, 0)))
        self.assertTrue(segments_intersect((0, 0), (1, 0), (1, 0), (2, 0)))
        self.assertFalse(segments_intersect((0, 0), (1, 0), (2, 0), (3, 0)))
        # Parallel but not collinear.
        self.assertFalse(segments_intersect((0, 0), (2, 0), (0, 1), (2, 1)))

    def test_random_vs_exact(self):
        rng = random.Random(123)
        for _ in range(5000):
            segs = [(rng.randint(-10, 10), rng.randint(-10, 10))
                    for _ in range(4)]
            self.assertEqual(segments_intersect(*segs),
                             exact_segments_intersect(*segs))


class TestSegmentIntersection(unittest.TestCase):
    def test_cross_point(self):
        kind, val = segment_intersection((0, 0), (2, 2), (0, 2), (2, 0))
        self.assertEqual(kind, "point")
        self.assertAlmostEqual(val[0], 1.0)
        self.assertAlmostEqual(val[1], 1.0)

    def test_touch_point(self):
        self.assertEqual(segment_intersection((0, 0), (1, 1), (1, 1), (2, 0)),
                         ("point", (1, 1)))

    def test_overlap(self):
        kind, val = segment_intersection((0, 0), (4, 0), (2, 0), (6, 0))
        self.assertEqual(kind, "segment")
        self.assertEqual(val, ((2, 0), (4, 0)))

    def test_overlap_single_point(self):
        self.assertEqual(segment_intersection((0, 0), (1, 0), (1, 0), (2, 0)),
                         ("point", (1, 0)))

    def test_disjoint(self):
        self.assertIsNone(segment_intersection((0, 0), (1, 0), (0, 1), (1, 1)))
        self.assertIsNone(segment_intersection((0, 0), (1, 0), (2, 0), (3, 0)))

    def test_contained(self):
        kind, val = segment_intersection((0, 0), (10, 0), (3, 0), (5, 0))
        self.assertEqual(kind, "segment")
        self.assertEqual(val, ((3, 0), (5, 0)))


if __name__ == "__main__":
    unittest.main()
