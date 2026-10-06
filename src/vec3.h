#pragma once

#include <cmath>
#include <ostream>

// Right-handed 3D vector. Used for points, directions and colors.
struct Vec3 {
    double x = 0.0;
    double y = 0.0;
    double z = 0.0;

    Vec3() = default;
    Vec3(double x_, double y_, double z_) : x(x_), y(y_), z(z_) {}

    Vec3 operator-() const { return Vec3(-x, -y, -z); }

    Vec3 operator+(const Vec3& o) const { return Vec3(x + o.x, y + o.y, z + o.z); }
    Vec3 operator-(const Vec3& o) const { return Vec3(x - o.x, y - o.y, z - o.z); }
    Vec3 operator*(const Vec3& o) const { return Vec3(x * o.x, y * o.y, z * o.z); }
    Vec3 operator*(double s) const { return Vec3(x * s, y * s, z * s); }
    Vec3 operator/(double s) const { return Vec3(x / s, y / s, z / s); }

    Vec3& operator+=(const Vec3& o) {
        x += o.x;
        y += o.y;
        z += o.z;
        return *this;
    }

    double dot(const Vec3& o) const { return x * o.x + y * o.y + z * o.z; }

    Vec3 cross(const Vec3& o) const {
        return Vec3(y * o.z - z * o.y, z * o.x - x * o.z, x * o.y - y * o.x);
    }

    double length() const { return std::sqrt(length_squared()); }
    double length_squared() const { return x * x + y * y + z * z; }

    Vec3 normalized() const {
        double len = length();
        return len > 0.0 ? *this / len : Vec3(0.0, 0.0, 0.0);
    }

    // Reflect this (incident) direction about unit normal n.
    Vec3 reflect(const Vec3& n) const { return *this - n * (2.0 * this->dot(n)); }
};

inline Vec3 operator*(double s, const Vec3& v) { return v * s; }

inline std::ostream& operator<<(std::ostream& os, const Vec3& v) {
    return os << "(" << v.x << ", " << v.y << ", " << v.z << ")";
}

using Point3 = Vec3;
using Color = Vec3;
