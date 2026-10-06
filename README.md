# CPU Ray Tracer

一个纯 CPU、零依赖的本地基础光线追踪器（C++17）。所有场景、几何体、
材质和输出图像仅存在于本地内存或文件中：不使用 GPU、游戏引擎、云渲染
或任何外部服务。输出为二进制 PPM（P6）图像，测试全部在终端运行，无需
显示窗口。

## 构建与运行

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j

# 渲染演示场景（宽 高 输出文件，参数均可省略）
./build/raytracer 640 360 output.ppm

# 运行测试（两种方式等价）
./build/raytracer_tests
ctest --test-dir build --output-on-failure
```

## 坐标系

- 世界坐标为**右手系**，Y 轴向上，相机默认朝 `-Z` 方向看。
- 相机由 `position`、`look_at`、`up`、垂直视场角 `vfov` 和宽高比定义；
  成像平面位于相机前方焦距 1 处，`(u, v) = (0, 0)` 对应图像左下角，
  `(0.5, 0.5)` 对应画面中心（中心主射线方向 = `normalize(look_at - position)`）。
- 图像行序：第 0 行为图像顶部（渲染时 `v = 1 - (y + 0.5) / height`）。

## 相交公式

射线定义为 `P(t) = O + t·D`，有效区间为 `t ∈ [t_min, t_max]`，
`kEpsilon = 1e-4` 作为 `t_min` 防止自相交（shadow acne）。

**球**（球心 `C`，半径 `r`）：令 `oc = O - C`，解

```
a = D·D,  half_b = oc·D,  c = oc·oc - r²
判别式 Δ = half_b² - a·c
```

- `Δ < 0`：不相交；`Δ = 0`：相切（唯一解）；`Δ > 0`：两解。
- 先取较近根 `t = (-half_b - √Δ) / a`，若不在有效区间（例如射线从球内
  发出）再取较远根 `(-half_b + √Δ) / a`。
- 命中记录包含 `t`、命中点、朝向外侧的单位法线（背面命中时翻转）。

**平面**（点 `P0`，单位法线 `N`）：

```
t = (P0 - O)·N / (D·N)
```

`D·N ≈ 0` 时射线与平面平行，无交点；命中法线根据射线来向翻转，
保证法线始终朝向入射侧。

场景级 `closest_hit` 遍历所有几何体，动态收缩 `t_max`，返回最近有效交点。

## 光照模型

环境光 + Lambert 漫反射 + Phong 高光，逐点光源累加：

```
C = ambient·ka·albedo
  + Σ_lights I·(kd·max(N·L, 0))·albedo        # Lambert 漫反射
  + Σ_lights I·(ks·max(R·V, 0)^shininess)     # Phong 高光
  + reflectivity · trace(reflect(D, N), depth+1)   # 镜面反射（递归）
```

- **Hard shadow**：从命中点沿法线偏移 `kEpsilon` 后向光源发射 shadow
  ray，若在 `[kEpsilon, 光源距离 - kEpsilon]` 内被任何几何体挡住，则该
  光源只贡献环境光（跳过漫反射与高光）。
- **镜面反射**：材质 `reflectivity ∈ [0, 1]`，反射射线同样沿法线偏移
  `kEpsilon` 出发；递归深度由 `Scene::max_depth` 限制（默认 4），
  达到上限后不再继续反射，避免无限递归。
- **自相交保护**：所有次级射线（shadow ray、反射 ray）的起点都沿法线
  偏移 `kEpsilon = 1e-4`，且求交 `t_min = kEpsilon`，消除表面自阴影
  条纹。

## 测试

`tests/test_raytracer.cpp` 为自带轻量断言框架的终端测试程序，覆盖：

- 射线-球体相交（穿心两解取最近）、相切（Δ=0）、不相交与球在射线背后
- 射线-平面相交及平行情形
- 多物体场景返回最近交点
- 相机中心主射线方向与左右对称性
- 硬阴影（遮挡点仅环境光、未遮挡点正常受光）
- 自相交 epsilon（受光表面不产生自阴影）
- 镜面反射递归深度限制（双面镜子场景必然终止，且结果随 max_depth 变化）
- 小分辨率（48×27）渲染的固定像素值与整图 FNV-1a 64 位哈希校验，
  保证渲染结果跨次运行完全确定

运行：

```bash
./build/raytracer_tests        # 直接运行，退出码非 0 表示失败
ctest --test-dir build         # 通过 CTest 运行
```

## 目录结构

```
src/vec3.h        三维向量/颜色数学
src/ray.h         射线定义
src/hittable.h    HitRecord、Sphere、Plane、kEpsilon
src/material.h    材质（albedo/ka/kd/ks/shininess/reflectivity）
src/light.h       点光源
src/camera.h      透视相机
src/scene.h       场景、最近交点、着色与递归追踪
src/image.h       RGB8 图像、PPM(P6) 输出、FNV-1a 哈希
src/demo_scene.h  演示场景与渲染循环（main 与测试共用）
src/main.cpp      渲染入口
tests/test_raytracer.cpp  终端自动化测试
```
