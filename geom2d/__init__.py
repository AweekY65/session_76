"""geom2d -- a small, self-contained 2D computational geometry library.

Everything runs locally in memory; no GIS services, databases or network
access of any kind.  See README.md for conventions and robustness policy.
"""

from .core import EPS
from .predicates import orientation, on_segment
from .segments import segments_intersect, segment_intersection
from .polygon import (signed_area2, area, polygon_orientation,
                      classify_point, point_in_polygon)
from .hull import convex_hull
from .clip import clip_convex

__all__ = [
    "EPS",
    "orientation",
    "on_segment",
    "segments_intersect",
    "segment_intersection",
    "signed_area2",
    "area",
    "polygon_orientation",
    "classify_point",
    "point_in_polygon",
    "convex_hull",
    "clip_convex",
]
