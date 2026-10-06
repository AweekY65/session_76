"""Segment-segment intersection, including collinear and endpoint contact."""

from .predicates import orientation, on_segment


def segments_intersect(p1, p2, p3, p4):
    """True iff closed segments p1p2 and p3p4 share at least one point.

    Proper crossings, endpoint touches and collinear overlaps all count.
    """
    d1 = orientation(p3, p4, p1)
    d2 = orientation(p3, p4, p2)
    d3 = orientation(p1, p2, p3)
    d4 = orientation(p1, p2, p4)
    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
       ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True
    return ((d1 == 0 and on_segment(p1, p3, p4))
            or (d2 == 0 and on_segment(p2, p3, p4))
            or (d3 == 0 and on_segment(p3, p1, p2))
            or (d4 == 0 and on_segment(p4, p1, p2)))


def segment_intersection(p1, p2, p3, p4):
    """Compute the intersection of closed segments p1p2 and p3p4.

    Returns one of:
      * ``None``                       -- disjoint
      * ``("point", (x, y))``          -- single common point (cross or touch)
      * ``("segment", (a, b))``        -- collinear overlap; a, b are the
        endpoints of the shared sub-segment in canonical sorted order
    """
    if not segments_intersect(p1, p2, p3, p4):
        return None

    d1 = orientation(p3, p4, p1)
    d2 = orientation(p3, p4, p2)
    d3 = orientation(p1, p2, p3)
    d4 = orientation(p1, p2, p4)

    if d1 == 0 and d2 == 0:
        # Collinear: project onto the dominant axis and intersect intervals.
        pts = [p1, p2, p3, p4]
        axis = 0 if abs(p2[0] - p1[0]) >= abs(p2[1] - p1[1]) else 1
        s = sorted([p1, p2], key=lambda p: (p[axis], p[1 - axis]))
        t = sorted([p3, p4], key=lambda p: (p[axis], p[1 - axis]))
        lo = max(s[0], t[0], key=lambda p: (p[axis], p[1 - axis]))
        hi = min(s[1], t[1], key=lambda p: (p[axis], p[1 - axis]))
        if lo == hi:
            return ("point", lo)
        return ("segment", (lo, hi))

    # Single-point intersection: report whichever endpoint touches, else
    # compute the proper crossing point of the two supporting lines.
    for d, p, q, r in ((d1, p1, p3, p4), (d2, p2, p3, p4),
                       (d3, p3, p1, p2), (d4, p4, p1, p2)):
        if d == 0:
            return ("point", p)

    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    px = ((x1 * y2 - y1 * x2) * (x3 - x4)
          - (x1 - x2) * (x3 * y4 - y3 * x4)) / den
    py = ((x1 * y2 - y1 * x2) * (y3 - y4)
          - (y1 - y2) * (x3 * y4 - y3 * x4)) / den
    return ("point", (px, py))
