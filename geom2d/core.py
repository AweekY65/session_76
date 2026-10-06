"""Core numeric policy for geom2d.

All algorithms in this package share the comparison helpers defined here so
that no two algorithms ever disagree about what "zero" means.

Coordinate convention
---------------------
Points are plain ``(x, y)`` tuples in a Cartesian plane (x right, y up).
Integers and floats may be mixed freely.

Robustness policy
-----------------
* If every coordinate involved in a predicate is an ``int``, the predicate is
  evaluated with exact integer arithmetic (no epsilon at all).
* Otherwise the predicate compares the (float) result against the single
  module-level absolute tolerance ``EPS``.
"""

EPS = 1e-9

# A point is any 2-sequence of numbers; tuples are used everywhere internally.
Point = tuple


def is_exact(*points):
    """True when every coordinate of every point is an int (exact mode)."""
    return all(isinstance(c, int) for p in points for c in p)


def sign(value):
    """Return -1, 0 or +1 for ``value`` under the unified robustness policy.

    Exact (int) values are compared to zero exactly; floats use ``EPS``.
    """
    if isinstance(value, int):
        return (value > 0) - (value < 0)
    if value > EPS:
        return 1
    if value < -EPS:
        return -1
    return 0


def cross(o, a, b):
    """2D cross product of vectors OA and OB (exact for int input)."""
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
