"""Simple-polygon algorithms: area, orientation, point location."""

from .core import EPS, sign
from .predicates import on_segment


def signed_area2(poly):
    """Twice the signed area; positive for CCW vertex order.

    Exact (int) when all coordinates are ints.
    """
    total = 0
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        total += x1 * y2 - x2 * y1
    return total


def area(poly):
    """Unsigned area of a simple polygon (0 for degenerate input)."""
    return abs(signed_area2(poly)) / 2


def polygon_orientation(poly):
    """'ccw', 'cw' or 'degenerate' (zero signed area under the EPS policy)."""
    s = sign(signed_area2(poly))
    if s > 0:
        return "ccw"
    if s < 0:
        return "cw"
    return "degenerate"


def classify_point(poly, p):
    """Locate point ``p`` relative to simple polygon ``poly``.

    Returns 'inside', 'boundary' or 'outside'.  A point exactly (within the
    unified EPS policy) on an edge or vertex is 'boundary'.  Uses the
    even-odd ray-casting rule after an explicit boundary pass.
    """
    n = len(poly)
    if n == 0:
        return "outside"
    if n == 1:
        return "boundary" if _points_equal(poly[0], p) else "outside"
    for i in range(n):
        if on_segment(p, poly[i], poly[(i + 1) % n]):
            return "boundary"
    if n == 2:
        return "outside"

    x, y = p
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y):
            x_int = xi + (y - yi) * (xj - xi) / (yj - yi)
            if x_int > x:
                inside = not inside
        j = i
    return "inside" if inside else "outside"


def point_in_polygon(poly, p, include_boundary=True):
    """True iff ``p`` is inside ``poly`` (boundary counts by default)."""
    c = classify_point(poly, p)
    if c == "boundary":
        return include_boundary
    return c == "inside"


def _points_equal(a, b):
    if isinstance(a[0], int) and isinstance(a[1], int) \
            and isinstance(b[0], int) and isinstance(b[1], int):
        return a == b
    return abs(a[0] - b[0]) <= EPS and abs(a[1] - b[1]) <= EPS
