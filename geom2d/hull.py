"""Convex hull via Andrew's monotone chain -- O(n log n), deterministic."""

from .predicates import orientation


def convex_hull(points, include_collinear=False):
    """Convex hull of ``points`` as a CCW vertex list starting at the
    lexicographically smallest point.

    Deterministic degenerate behaviour:
      * duplicate points are removed;
      * fewer than 3 unique points -> the sorted unique points themselves;
      * all points collinear -> the two extreme endpoints
        (or, with ``include_collinear=True``, every collinear point along
        the boundary, out and back).

    With ``include_collinear=False`` (default) collinear points on hull
    edges are dropped so only true vertices remain.
    """
    pts = sorted(set(map(tuple, points)))
    if len(pts) <= 2:
        return pts

    def build(cmp):
        lower, upper = [], []
        for p in pts:
            while len(lower) >= 2 and cmp(orientation(lower[-2], lower[-1], p)):
                lower.pop()
            lower.append(p)
        for p in reversed(pts):
            while len(upper) >= 2 and cmp(orientation(upper[-2], upper[-1], p)):
                upper.pop()
            upper.append(p)
        return lower[:-1] + upper[:-1]

    if include_collinear:
        return build(lambda o: o < 0)
    return build(lambda o: o <= 0)
