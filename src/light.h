#pragma once

#include "vec3.h"

struct PointLight {
    Point3 position;
    Color intensity{1.0, 1.0, 1.0};
};
