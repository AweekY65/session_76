#pragma once

#include <algorithm>
#include <cstdint>
#include <fstream>
#include <stdexcept>
#include <vector>

#include "vec3.h"

// Simple RGB8 image with binary PPM (P6) output.
struct Image {
    int width = 0;
    int height = 0;
    std::vector<uint8_t> pixels;  // RGBRGB..., row 0 = top scanline

    Image(int w, int h) : width(w), height(h), pixels(static_cast<size_t>(w) * h * 3, 0) {}

    static uint8_t to_byte(double v) {
        v = std::clamp(v, 0.0, 1.0);
        return static_cast<uint8_t>(v * 255.0 + 0.5);
    }

    // row 0 is the top of the image.
    void set_pixel(int x, int y_from_top, const Color& c) {
        size_t idx = (static_cast<size_t>(y_from_top) * width + x) * 3;
        pixels[idx + 0] = to_byte(c.x);
        pixels[idx + 1] = to_byte(c.y);
        pixels[idx + 2] = to_byte(c.z);
    }

    Color get_pixel(int x, int y_from_top) const {
        size_t idx = (static_cast<size_t>(y_from_top) * width + x) * 3;
        return Color(pixels[idx] / 255.0, pixels[idx + 1] / 255.0, pixels[idx + 2] / 255.0);
    }

    void write_ppm(const std::string& path) const {
        std::ofstream out(path, std::ios::binary);
        if (!out) throw std::runtime_error("cannot open output file: " + path);
        out << "P6\n" << width << " " << height << "\n255\n";
        out.write(reinterpret_cast<const char*>(pixels.data()),
                  static_cast<std::streamsize>(pixels.size()));
    }

    // FNV-1a 64-bit hash over the raw pixel bytes (deterministic checksum).
    uint64_t hash() const {
        uint64_t h = 14695981039346656037ull;
        for (uint8_t b : pixels) {
            h ^= b;
            h *= 1099511628211ull;
        }
        return h;
    }
};
