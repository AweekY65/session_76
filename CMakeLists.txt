cmake_minimum_required(VERSION 3.16)
project(cpu_raytracer CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

add_compile_options(-Wall -Wextra)

add_executable(raytracer src/main.cpp)
target_include_directories(raytracer PRIVATE src)

add_executable(raytracer_tests tests/test_raytracer.cpp)
target_include_directories(raytracer_tests PRIVATE src)

enable_testing()
add_test(NAME raytracer_tests COMMAND raytracer_tests)
