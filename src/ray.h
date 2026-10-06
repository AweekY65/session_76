#pragma once

#include "vec3.h"

// A ray: P(t) = origin + t * direction, valid for t >= 0.
struct Ray {
    Point3 origin;
    Vec3 direction; // expected to be normalized by convention

    Ray() = default;
    Ray(const Point3& o, const Vec3& d) : origin(o), direction(d) {}

    Point3 at(double t) const { return origin + direction * t; }
};
