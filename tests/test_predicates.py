import random
import unittest

from geom2d import orientation, on_segment
from tests.brute import exact_orientation, exact_on_segment


class TestOrientation(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(orientation((0, 0), (1, 0), (0, 1)), 1)   # ccw
        self.assertEqual(orientation((0, 0), (0, 1), (1, 0)), -1)  # cw
        self.assertEqual(orientation((0, 0), (1, 1), (2, 2)), 0)   # collinear

    def test_exact_integers_large(self):
        # Values whose float cross product would lose precision.
        a = (0, 0)
        b = (10**9, 1)
        c = (10**9 + 1, 1)
        self.assertEqual(orientation(a, b, c), -1)
        self.assertEqual(orientation(a, b, (10**9, 1)), 0)

    def test_float_epsilon(self):
        self.assertEqual(orientation((0.0, 0.0), (1.0, 0.0), (0.5, 1e-12)), 0)
        self.assertEqual(orientation((0.0, 0.0), (1.0, 0.0), (0.5, 1e-6)), 1)

    def test_random_vs_exact(self):
        rng = random.Random(42)
        for _ in range(2000):
            pts = [(rng.randint(-50, 50), rng.randint(-50, 50))
                   for _ in range(3)]
            self.assertEqual(orientation(*pts), exact_orientation(*pts))


class TestOnSegment(unittest.TestCase):
    def test_interior_and_endpoints(self):
        self.assertTrue(on_segment((1, 1), (0, 0), (2, 2)))
        self.assertTrue(on_segment((0, 0), (0, 0), (2, 2)))
        self.assertTrue(on_segment((2, 2), (0, 0), (2, 2)))

    def test_off_segment(self):
        self.assertFalse(on_segment((1, 2), (0, 0), (2, 2)))
        self.assertFalse(on_segment((3, 3), (0, 0), (2, 2)))  # collinear, out

    def test_degenerate_segment(self):
        self.assertTrue(on_segment((1, 1), (1, 1), (1, 1)))
        self.assertFalse(on_segment((1, 2), (1, 1), (1, 1)))

    def test_random_vs_exact(self):
        rng = random.Random(7)
        for _ in range(2000):
            a = (rng.randint(-20, 20), rng.randint(-20, 20))
            b = (rng.randint(-20, 20), rng.randint(-20, 20))
            # Mix arbitrary points with points constructed on the segment.
            if rng.random() < 0.5:
                t = rng.randint(-2, 3)
                p = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
            else:
                p = (rng.randint(-20, 20), rng.randint(-20, 20))
            self.assertEqual(on_segment(p, a, b), exact_on_segment(p, a, b))


if __name__ == "__main__":
    unittest.main()
