#include <cstdlib>
#include <iostream>
#include <string>

#include "demo_scene.h"

int main(int argc, char** argv) {
    int width = 640;
    int height = 360;
    std::string output = "output.ppm";
    if (argc > 1) width = std::atoi(argv[1]);
    if (argc > 2) height = std::atoi(argv[2]);
    if (argc > 3) output = argv[3];

    Scene scene = make_demo_scene();
    Camera camera = make_demo_camera(width, height);
    Image img = render(scene, camera, width, height);
    img.write_ppm(output);

    std::cout << "Wrote " << output << " (" << width << "x" << height << ")\n";
    std::cout << "Pixel hash (FNV-1a64): " << img.hash() << "\n";
    return 0;
}
