"""Independent brute-force reference implementations used only by tests.

Everything here uses exact Fraction arithmetic so the library's float
results can be cross-validated without sharing any code with geom2d.
"""

from fractions import Fraction


def fpt(p):
    return (Fraction(p[0]), Fraction(p[1]))


def exact_cross(o, a, b):
    o, a, b = fpt(o), fpt(a), fpt(b)
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def exact_sign(v):
    return (v > 0) - (v < 0)


def exact_orientation(a, b, c):
    return exact_sign(exact_cross(a, b, c))


def exact_on_segment(p, a, b):
    p, a, b = fpt(p), fpt(a), fpt(b)
    if exact_cross(a, b, p) != 0:
        return False
    return (min(a[0], b[0]) <= p[0] <= max(a[0], b[0])
            and min(a[1], b[1]) <= p[1] <= max(a[1], b[1]))


def exact_segments_intersect(p1, p2, p3, p4):
    d1 = exact_orientation(p3, p4, p1)
    d2 = exact_orientation(p3, p4, p2)
    d3 = exact_orientation(p1, p2, p3)
    d4 = exact_orientation(p1, p2, p4)
    if d1 * d2 < 0 and d3 * d4 < 0:
        return True
    return ((d1 == 0 and exact_on_segment(p1, p3, p4))
            or (d2 == 0 and exact_on_segment(p2, p3, p4))
            or (d3 == 0 and exact_on_segment(p3, p1, p2))
            or (d4 == 0 and exact_on_segment(p4, p1, p2)))


def exact_point_in_polygon(poly, p):
    """Even-odd rule with exact arithmetic; boundary reported separately."""
    p = fpt(p)
    poly = [fpt(q) for q in poly]
    n = len(poly)
    for i in range(n):
        if exact_on_segment(p, poly[i], poly[(i + 1) % n]):
            return "boundary"
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


def brute_hull_vertices(points):
    """Set of points that are extreme: p is a hull vertex iff it is not in
    the convex hull of the remaining points (Caratheodory in 2D: inside a
    triangle of, or on a segment between, other points)."""
    pts = sorted(set(map(tuple, points)))
    n = len(pts)
    if n <= 2:
        return set(pts)
    extreme = set()
    for i, p in enumerate(pts):
        rest = pts[:i] + pts[i + 1:]
        inside = False
        m = len(rest)
        for a in range(m):
            if inside:
                break
            for b in range(a + 1, m):
                if exact_on_segment(p, rest[a], rest[b]):
                    inside = True
                    break
                for c in range(b + 1, m):
                    if exact_orientation(rest[a], rest[b], rest[c]) == 0:
                        continue  # degenerate triangle; covered by seg check
                    s1 = exact_orientation(rest[a], rest[b], p)
                    s2 = exact_orientation(rest[b], rest[c], p)
                    s3 = exact_orientation(rest[c], rest[a], p)
                    if (s1 >= 0 and s2 >= 0 and s3 >= 0) or \
                       (s1 <= 0 and s2 <= 0 and s3 <= 0):
                        inside = True
                        break
                if inside:
                    break
        if not inside:
            extreme.add(p)
    return extreme


def star_polygon(points):
    """Build a simple (star-shaped) polygon by sorting points angularly
    around their centroid -- used to generate random simple polygons."""
    import math
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    return sorted(points, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
