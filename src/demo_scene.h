#pragma once

#include "camera.h"
#include "image.h"
#include "scene.h"

// Builds the deterministic demo scene shared by the renderer and the tests.
inline Scene make_demo_scene() {
    Scene scene;
    scene.background = Color(0.05, 0.07, 0.10);
    scene.ambient = Color(1.0, 1.0, 1.0);
    scene.max_depth = 4;

    Material ground;
    ground.albedo = Color(0.7, 0.7, 0.7);
    ground.ka = 0.1; ground.kd = 0.8; ground.ks = 0.1; ground.shininess = 16.0;
    ground.reflectivity = 0.2;

    Material red;
    red.albedo = Color(0.9, 0.2, 0.2);
    red.ka = 0.1; red.kd = 0.8; red.ks = 0.4; red.shininess = 64.0;

    Material mirror;
    mirror.albedo = Color(0.85, 0.85, 0.9);
    mirror.ka = 0.05; mirror.kd = 0.2; mirror.ks = 0.8; mirror.shininess = 128.0;
    mirror.reflectivity = 0.7;

    int ground_id = scene.add_material(ground);
    int red_id = scene.add_material(red);
    int mirror_id = scene.add_material(mirror);

    scene.add_object(std::make_shared<Plane>(Point3(0, -1, 0), Vec3(0, 1, 0), ground_id));
    scene.add_object(std::make_shared<Sphere>(Point3(-1.2, 0.0, -4.0), 1.0, red_id));
    scene.add_object(std::make_shared<Sphere>(Point3(1.2, 0.2, -5.0), 1.2, mirror_id));

    scene.add_light(PointLight{Point3(5, 8, 2), Color(1.0, 1.0, 1.0)});
    return scene;
}

inline Camera make_demo_camera(int width, int height) {
    double aspect = static_cast<double>(width) / static_cast<double>(height);
    return Camera(Point3(0, 1, 3), Point3(0, 0, -4), Vec3(0, 1, 0), 45.0, aspect);
}

// Renders the scene; pixel (0,0) is the top-left corner.
inline Image render(const Scene& scene, const Camera& camera, int width, int height) {
    Image img(width, height);
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            double u = (x + 0.5) / width;
            double v = 1.0 - (y + 0.5) / height;
            img.set_pixel(x, y, scene.trace(camera.generate_ray(u, v)));
        }
    }
    return img;
}
