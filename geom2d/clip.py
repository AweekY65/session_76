"""Convex polygon clipping (Sutherland-Hodgman)."""

from .core import sign
from .predicates import orientation
from .polygon import polygon_orientation


def clip_convex(subject, clip):
    """Intersect simple polygon ``subject`` with convex polygon ``clip``.

    Returns the clipped polygon as a vertex list.  The output order is
    stable: vertices follow the subject polygon's traversal order, and the
    result is empty (``[]``) when the intersection has zero area.  Clip-edge
    boundaries are inclusive, so a subject edge lying on a clip edge is
    kept.
    """
    if len(clip) < 3 or len(subject) < 3:
        return []
    wind = 1 if polygon_orientation(clip) == "ccw" else -1

    def inside(p, a, b):
        return wind * orientation(a, b, p) >= 0

    def line_intersection(s, e, a, b):
        # Point where segment s->e crosses the supporting line of edge a->b.
        d1 = (b[0] - a[0]) * (s[1] - a[1]) - (b[1] - a[1]) * (s[0] - a[0])
        d2 = (b[0] - a[0]) * (e[1] - a[1]) - (b[1] - a[1]) * (e[0] - a[0])
        den = d1 - d2
        if sign(den) == 0:
            return e  # segment parallel to clip edge; keep the endpoint
        t = d1 / den
        return (s[0] + t * (e[0] - s[0]), s[1] + t * (e[1] - s[1]))

    output = list(subject)
    n = len(clip)
    for i in range(n):
        a, b = clip[i], clip[(i + 1) % n]
        if not output:
            break
        inp = output
        output = []
        s = inp[-1]
        for e in inp:
            if inside(e, a, b):
                if not inside(s, a, b):
                    output.append(line_intersection(s, e, a, b))
                output.append(e)
            elif inside(s, a, b):
                output.append(line_intersection(s, e, a, b))
            s = e
    return output
