"""Fundamental geometric predicates: orientation and point-on-segment."""

from .core import cross, sign


def orientation(a, b, c):
    """Orientation of the ordered triple (a, b, c).

    Returns +1 for counter-clockwise (left turn), -1 for clockwise
    (right turn) and 0 for collinear, using the unified robustness policy
    from :mod:`geom2d.core`.
    """
    return sign(cross(a, b, c))


def on_segment(p, a, b):
    """True iff point ``p`` lies on the closed segment ``ab``.

    Collinearity and the bounding-box test both use the unified policy, so a
    point within ``EPS`` of the segment counts as on it in float mode.
    """
    if orientation(a, b, p) != 0:
        return False
    if all(isinstance(c, int) for q in (p, a, b) for c in q):
        return (min(a[0], b[0]) <= p[0] <= max(a[0], b[0])
                and min(a[1], b[1]) <= p[1] <= max(a[1], b[1]))
    from .core import EPS
    return (min(a[0], b[0]) - EPS <= p[0] <= max(a[0], b[0]) + EPS
            and min(a[1], b[1]) - EPS <= p[1] <= max(a[1], b[1]) + EPS)
