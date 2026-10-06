#pragma once

#include "vec3.h"

// Blinn-Phong-style material with ambient/diffuse/specular terms and a
// mirror reflectivity coefficient in [0, 1].
struct Material {
    Color albedo{0.8, 0.8, 0.8}; // base surface color
    double ka = 0.1;             // ambient coefficient
    double kd = 0.7;             // Lambert diffuse coefficient
    double ks = 0.3;             // Phong specular coefficient
    double shininess = 32.0;     // Phong exponent
    double reflectivity = 0.0;   // 0 = matte, 1 = perfect mirror
};
