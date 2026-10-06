#pragma once

#include <cmath>

#include "ray.h"

// Pinhole perspective camera. Right-handed, y-up world; the camera looks
// from `position` toward `look_at` (forward = normalize(look_at - position)).
class Camera {
  public:
    Camera(Point3 position, Point3 look_at, Vec3 up, double vfov_degrees, double aspect_ratio) {
        double theta = vfov_degrees * M_PI / 180.0;
        double half_h = std::tan(theta / 2.0);
        double half_w = aspect_ratio * half_h;

        forward_ = (look_at - position).normalized();
        right_ = forward_.cross(up).normalized();
        up_ = right_.cross(forward_).normalized();

        origin_ = position;
        horizontal_ = right_ * (2.0 * half_w);
        vertical_ = up_ * (2.0 * half_h);
        lower_left_ = origin_ + forward_ - horizontal_ / 2.0 - vertical_ / 2.0;
    }

    // u, v in [0, 1]: (0,0) is the lower-left image corner, (0.5,0.5) the center.
    Ray generate_ray(double u, double v) const {
        Vec3 target = lower_left_ + horizontal_ * u + vertical_ * v;
        return Ray(origin_, (target - origin_).normalized());
    }

    const Point3& origin() const { return origin_; }
    const Vec3& forward() const { return forward_; }

  private:
    Point3 origin_;
    Vec3 forward_, right_, up_;
    Vec3 horizontal_, vertical_, lower_left_;
};
