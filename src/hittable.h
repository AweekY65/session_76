#pragma once

#include <memory>
#include <optional>
#include <vector>

#include "material.h"
#include "ray.h"

// Epsilon used to avoid self-intersection ("shadow acne") when spawning
// secondary rays (shadow rays, reflection rays).
constexpr double kEpsilon = 1e-4;

struct HitRecord {
    double t = 0.0;        // ray parameter of the hit
    Point3 point;          // world-space hit point
    Vec3 normal;           // unit surface normal, oriented against the ray
    int material_id = -1;  // index into the scene material table
    bool front_face = true;
};

class Hittable {
  public:
    virtual ~Hittable() = default;
    // Returns the nearest intersection with t in [t_min, t_max], if any.
    virtual std::optional<HitRecord> hit(const Ray& ray, double t_min, double t_max) const = 0;
};

// Sphere defined by center, radius and a material index.
class Sphere : public Hittable {
  public:
    Sphere(Point3 center, double radius, int material_id)
        : center_(center), radius_(radius), material_id_(material_id) {}

    std::optional<HitRecord> hit(const Ray& ray, double t_min, double t_max) const override {
        // Solve |o + t d - c|^2 = r^2  ->  a t^2 + 2 h t + c = 0
        Vec3 oc = ray.origin - center_;
        double a = ray.direction.length_squared();
        double half_b = oc.dot(ray.direction);
        double c = oc.length_squared() - radius_ * radius_;
        double discriminant = half_b * half_b - a * c;
        if (discriminant < 0.0) return std::nullopt;  // miss (tangent => disc == 0)

        double sqrt_d = std::sqrt(discriminant);
        // Nearest root first, then the far root (ray starting inside).
        double root = (-half_b - sqrt_d) / a;
        if (root < t_min || root > t_max) {
            root = (-half_b + sqrt_d) / a;
            if (root < t_min || root > t_max) return std::nullopt;
        }

        HitRecord rec;
        rec.t = root;
        rec.point = ray.at(root);
        Vec3 outward = (rec.point - center_) / radius_;
        rec.front_face = ray.direction.dot(outward) < 0.0;
        rec.normal = rec.front_face ? outward : -outward;
        rec.material_id = material_id_;
        return rec;
    }

  private:
    Point3 center_;
    double radius_;
    int material_id_;
};

// Infinite plane defined by a point and a (normalized) normal.
class Plane : public Hittable {
  public:
    Plane(Point3 point, Vec3 normal, int material_id)
        : point_(point), normal_(normal.normalized()), material_id_(material_id) {}

    std::optional<HitRecord> hit(const Ray& ray, double t_min, double t_max) const override {
        // t = dot(p0 - o, n) / dot(d, n)
        double denom = normal_.dot(ray.direction);
        if (std::fabs(denom) < 1e-12) return std::nullopt;  // parallel
        double t = (point_ - ray.origin).dot(normal_) / denom;
        if (t < t_min || t > t_max) return std::nullopt;

        HitRecord rec;
        rec.t = t;
        rec.point = ray.at(t);
        rec.front_face = denom < 0.0;
        rec.normal = rec.front_face ? normal_ : -normal_;
        rec.material_id = material_id_;
        return rec;
    }

  private:
    Point3 point_;
    Vec3 normal_;
    int material_id_;
};
