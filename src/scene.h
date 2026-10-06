#pragma once

#include <memory>
#include <optional>
#include <vector>

#include "camera.h"
#include "hittable.h"
#include "light.h"

class Scene {
  public:
    Color background{0.0, 0.0, 0.0};
    Color ambient{0.1, 0.1, 0.1};
    int max_depth = 4;

    int add_material(const Material& m) {
        materials.push_back(m);
        return static_cast<int>(materials.size()) - 1;
    }
    void add_object(std::shared_ptr<Hittable> obj) { objects.push_back(std::move(obj)); }
    void add_light(const PointLight& l) { lights.push_back(l); }

    // Nearest hit among all objects with t in [t_min, t_max].
    std::optional<HitRecord> closest_hit(const Ray& ray, double t_min, double t_max) const {
        std::optional<HitRecord> best;
        double closest = t_max;
        for (const auto& obj : objects) {
            if (auto rec = obj->hit(ray, t_min, closest)) {
                closest = rec->t;
                best = rec;
            }
        }
        return best;
    }

    // Trace a ray, returning the shaded color. Recurses for mirror
    // reflections up to max_depth additional bounces.
    Color trace(const Ray& ray, int depth = 0) const {
        auto hit = closest_hit(ray, kEpsilon, 1e30);
        if (!hit) return background;

        const Material& mat = materials.at(static_cast<size_t>(hit->material_id));
        const Vec3 n = hit->normal;
        const Vec3 view_dir = -ray.direction;  // toward the camera

        // Ambient term.
        Color color = ambient * mat.ka * mat.albedo;

        for (const auto& light : lights) {
            Vec3 to_light = light.position - hit->point;
            double light_dist = to_light.length();
            Vec3 light_dir = to_light / light_dist;

            // Hard shadow: occluded if anything blocks the segment to the light.
            Ray shadow_ray(hit->point + n * kEpsilon, light_dir);
            if (closest_hit(shadow_ray, kEpsilon, light_dist - kEpsilon)) continue;

            // Lambert diffuse.
            double ndotl = n.dot(light_dir);
            if (ndotl > 0.0)
                color += light.intensity * (mat.kd * ndotl) * mat.albedo;

            // Phong specular.
            Vec3 reflect_dir = (-light_dir).reflect(n);
            double rdotv = reflect_dir.dot(view_dir);
            if (rdotv > 0.0)
                color += light.intensity * (mat.ks * std::pow(rdotv, mat.shininess));
        }

        // Mirror reflection with recursion depth limit.
        if (mat.reflectivity > 0.0 && depth < max_depth) {
            Vec3 refl_dir = ray.direction.reflect(n);
            Ray refl_ray(hit->point + n * kEpsilon, refl_dir);
            color += trace(refl_ray, depth + 1) * mat.reflectivity;
        }

        return color;
    }

    std::vector<Material> materials;
    std::vector<std::shared_ptr<Hittable>> objects;
    std::vector<PointLight> lights;
};
