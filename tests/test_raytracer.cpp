// Terminal-run unit tests for the CPU ray tracer. No window, no GPU.
#include <cmath>
#include <cstdint>
#include <iostream>
#include <memory>
#include <string>

#include "../src/demo_scene.h"

static int g_failures = 0;
static int g_checks = 0;

#define CHECK(cond)                                                        \
    do {                                                                   \
        ++g_checks;                                                        \
        if (!(cond)) {                                                     \
            ++g_failures;                                                  \
            std::cerr << "FAIL " << __FILE__ << ":" << __LINE__ << "  "    \
                      << #cond << "\n";                                    \
        }                                                                  \
    } while (0)

static bool near(double a, double b, double eps = 1e-9) {
    return std::fabs(a - b) <= eps;
}

static bool vec_near(const Vec3& a, const Vec3& b, double eps = 1e-9) {
    return near(a.x, b.x, eps) && near(a.y, b.y, eps) && near(a.z, b.z, eps);
}

// 1) Ray-sphere: straight hit through the center gives two roots; the
//    nearest valid one must be returned.
static void test_sphere_hit() {
    Sphere s(Point3(0, 0, -5), 1.0, 0);
    Ray r(Point3(0, 0, 0), Vec3(0, 0, -1));
    auto hit = s.hit(r, kEpsilon, 1e30);
    CHECK(hit.has_value());
    CHECK(hit && near(hit->t, 4.0));
    CHECK(hit && vec_near(hit->point, Vec3(0, 0, -4)));
    CHECK(hit && vec_near(hit->normal, Vec3(0, 0, 1)));
    CHECK(hit && hit->front_face);
}

// 2) Ray-sphere: tangent ray (discriminant == 0) yields exactly one hit.
static void test_sphere_tangent() {
    Sphere s(Point3(0, 0, -5), 1.0, 0);
    Ray r(Point3(1, 0, 0), Vec3(0, 0, -1));
    auto hit = s.hit(r, kEpsilon, 1e30);
    CHECK(hit.has_value());
    CHECK(hit && near(hit->t, 5.0));
    CHECK(hit && vec_near(hit->point, Vec3(1, 0, -5)));
}

// 3) Ray-sphere: a ray missing the sphere returns no hit.
static void test_sphere_miss() {
    Sphere s(Point3(0, 0, -5), 1.0, 0);
    Ray r(Point3(2, 0, 0), Vec3(0, 0, -1));
    CHECK(!s.hit(r, kEpsilon, 1e30).has_value());
    // Sphere fully behind the ray origin must not be reported either.
    Ray backward(Point3(0, 0, 0), Vec3(0, 0, 1));
    CHECK(!s.hit(backward, kEpsilon, 1e30).has_value());
}

// 4) Plane intersection, including the parallel case.
static void test_plane_hit() {
    Plane p(Point3(0, -1, 0), Vec3(0, 1, 0), 0);
    Ray down(Point3(0, 1, 0), Vec3(0, -1, 0));
    auto hit = p.hit(down, kEpsilon, 1e30);
    CHECK(hit.has_value());
    CHECK(hit && near(hit->t, 2.0));
    CHECK(hit && vec_near(hit->normal, Vec3(0, 1, 0)));
    Ray parallel(Point3(0, 1, 0), Vec3(1, 0, 0));
    CHECK(!p.hit(parallel, kEpsilon, 1e30).has_value());
}

// 5) Nearest hit: with two spheres along the ray, the closer one wins.
static void test_closest_hit() {
    Scene scene;
    int m = scene.add_material(Material{});
    scene.add_object(std::make_shared<Sphere>(Point3(0, 0, -8), 1.0, m));
    scene.add_object(std::make_shared<Sphere>(Point3(0, 0, -4), 1.0, m));
    Ray r(Point3(0, 0, 0), Vec3(0, 0, -1));
    auto hit = scene.closest_hit(r, kEpsilon, 1e30);
    CHECK(hit.has_value());
    CHECK(hit && near(hit->t, 3.0));  // near sphere surface, not the far one
}

// 6) Camera: the center ray (u=v=0.5) travels along the forward axis.
static void test_camera_center_ray() {
    Camera cam(Point3(0, 1, 3), Point3(0, 0, -4), Vec3(0, 1, 0), 45.0, 16.0 / 9.0);
    Ray center = cam.generate_ray(0.5, 0.5);
    CHECK(vec_near(center.origin, Vec3(0, 1, 3)));
    Vec3 expected = (Vec3(0, 0, -4) - Vec3(0, 1, 3)).normalized();
    CHECK(vec_near(center.direction, expected, 1e-9));
    // Corner rays must be symmetric about the center ray.
    Ray ll = cam.generate_ray(0.0, 0.0);
    Ray lr = cam.generate_ray(1.0, 0.0);
    CHECK(near(ll.direction.y, lr.direction.y, 1e-9));
    CHECK(near(ll.direction.x, -lr.direction.x, 1e-9));
}

// 7) Hard shadow: a point occluded from the light receives ambient only,
//    while an unoccluded point is fully lit.
static void test_shadow() {
    Scene scene;
    scene.ambient = Color(1, 1, 1);
    scene.background = Color(0, 0, 0);
    Material mat;
    mat.albedo = Color(1, 1, 1);
    mat.ka = 0.2; mat.kd = 1.0; mat.ks = 0.0;
    int ground = scene.add_material(mat);
    int blocker = scene.add_material(mat);
    scene.add_object(std::make_shared<Plane>(Point3(0, 0, 0), Vec3(0, 1, 0), ground));
    // Opaque sphere between the shaded point and the light.
    scene.add_object(std::make_shared<Sphere>(Point3(0, 2, 0), 0.5, blocker));
    scene.add_light(PointLight{Point3(0, 4, 0), Color(1, 1, 1)});

    // Ray onto the plane point directly under the blocker sphere, arriving
    // from the side so the primary ray itself misses the sphere.
    Vec3 dir = (Vec3(0, 0, 0) - Vec3(0, 1, 5)).normalized();
    Color shaded = scene.trace(Ray(Point3(0, 1, 5), dir));
    CHECK(near(shaded.x, 0.2, 1e-9));  // ambient only: ka * albedo
    // Off to the side the point is lit: ambient + diffuse.
    Color lit = scene.trace(Ray(Point3(3, 5, 0), Vec3(0, -1, 0)));
    CHECK(lit.x > 0.5);
}

// 8) Self-intersection epsilon: a lit surface point must not shadow itself.
static void test_no_self_shadow() {
    Scene scene;
    scene.ambient = Color(0, 0, 0);
    scene.background = Color(0, 0, 0);
    Material mat;
    mat.albedo = Color(1, 1, 1);
    mat.ka = 0.0; mat.kd = 1.0; mat.ks = 0.0;
    int m = scene.add_material(mat);
    scene.add_object(std::make_shared<Plane>(Point3(0, 0, 0), Vec3(0, 1, 0), m));
    scene.add_light(PointLight{Point3(0, 4, 0), Color(1, 1, 1)});
    Color c = scene.trace(Ray(Point3(0, 5, 0), Vec3(0, -1, 0)));
    CHECK(near(c.x, 1.0, 1e-9));  // full diffuse, no acne darkening
}

// 9) Reflection recursion limit: two facing perfect mirrors must terminate,
//    and the result must depend on max_depth (i.e. the limit is honored).
static void test_reflection_depth_limit() {
    auto build = [](int max_depth) {
        Scene scene;
        scene.ambient = Color(0, 0, 0);
        scene.background = Color(0, 0, 0);
        scene.max_depth = max_depth;
        Material mirror;
        mirror.albedo = Color(0, 0, 0);
        mirror.ka = 0.0; mirror.kd = 0.0; mirror.ks = 0.0;
        mirror.reflectivity = 1.0;
        int m = scene.add_material(mirror);
        scene.add_object(std::make_shared<Plane>(Point3(0, 0, -1), Vec3(0, 0, 1), m));
        scene.add_object(std::make_shared<Plane>(Point3(0, 0, 1), Vec3(0, 0, -1), m));
        return scene;
    };
    // Terminates for any depth (the test itself finishing proves it).
    Color d0 = build(0).trace(Ray(Point3(0, 0, 0), Vec3(0, 0, -1)));
    Color d4 = build(4).trace(Ray(Point3(0, 0, 0), Vec3(0, 0, -1)));
    CHECK(std::isfinite(d0.x) && std::isfinite(d4.x));
    // Pure black mirrors: still black, but recursion must not hang/crash.
    CHECK(near(d0.x, 0.0) && near(d4.x, 0.0));

    // A mirror facing a lit diffuse wall: deeper recursion must change the
    // result, proving reflections actually recurse up to the depth limit.
    Scene scene;
    scene.ambient = Color(0, 0, 0);
    scene.background = Color(0, 0, 0);
    Material mirror;
    mirror.albedo = Color(0, 0, 0);
    mirror.ka = 0.0; mirror.kd = 0.0; mirror.ks = 0.0;
    mirror.reflectivity = 1.0;
    Material diffuse;
    diffuse.albedo = Color(1, 0, 0);
    diffuse.ka = 0.0; diffuse.kd = 1.0; diffuse.ks = 0.0;
    int mm = scene.add_material(mirror);
    int dm = scene.add_material(diffuse);
    scene.add_object(std::make_shared<Plane>(Point3(0, 0, -1), Vec3(0, 0, 1), mm));
    scene.add_object(std::make_shared<Plane>(Point3(0, 0, 1), Vec3(0, 0, -1), dm));
    scene.add_light(PointLight{Point3(0, 0, 0.5), Color(1, 1, 1)});
    Ray r(Point3(0, 0, 0), Vec3(0, 0, -1));
    scene.max_depth = 0;
    Color no_bounce = scene.trace(r);
    scene.max_depth = 2;
    Color bounced = scene.trace(r);
    CHECK(near(no_bounce.x, 0.0));   // depth 0: mirror reflects nothing
    CHECK(bounced.x > 0.0);          // recursion picks up the red wall
}

// 10) Deterministic render: fixed pixel values and a fixed whole-image hash
//     for a small resolution render of the demo scene.
static void test_render_hash() {
    const int W = 48, H = 27;
    Scene scene = make_demo_scene();
    Camera cam = make_demo_camera(W, H);
    Image img = render(scene, cam, W, H);

    // Fixed pixels (byte values, top-left origin).
    auto px = [&](int x, int y) {
        size_t i = (static_cast<size_t>(y) * W + x) * 3;
        return std::string{reinterpret_cast<char*>(&img.pixels[i]), 3};
    };
    CHECK(px(24, 13) == std::string("\x58\x59\x5a", 3));  // image center
    CHECK(px(0, 0) == std::string("\x0d\x12\x1a", 3));    // top-left sky
    CHECK(img.hash() == 0x0c675a7dbfad6827ull);
}

int main() {
    test_sphere_hit();
    test_sphere_tangent();
    test_sphere_miss();
    test_plane_hit();
    test_closest_hit();
    test_camera_center_ray();
    test_shadow();
    test_no_self_shadow();
    test_reflection_depth_limit();
    test_render_hash();

    std::cout << (g_checks - g_failures) << "/" << g_checks << " checks passed\n";
    if (g_failures > 0) {
        std::cerr << g_failures << " check(s) FAILED\n";
        return 1;
    }
    std::cout << "ALL TESTS PASSED\n";
    return 0;
}
