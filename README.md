# geom2d — 本地二维计算几何库

纯 Python 标准库实现，所有几何数据、测试输入与结果只存在于本地文件或
内存中。**不依赖** GIS 服务、数据库、云计算或任何外部服务/第三方包。

## 功能

| 模块 | 内容 |
|---|---|
| `geom2d.predicates` | `orientation`（点定向）、`on_segment`（点在线段上） |
| `geom2d.segments` | `segments_intersect`、`segment_intersection`（含共线重叠与端点接触） |
| `geom2d.polygon` | `area` / `signed_area2`、`polygon_orientation`、`classify_point` / `point_in_polygon` |
| `geom2d.hull` | `convex_hull`（Andrew 单调链，O(n log n)） |
| `geom2d.clip` | `clip_convex`（Sutherland–Hodgman 凸多边形裁剪） |

## 坐标约定

- 点为 `(x, y)` 元组，笛卡尔平面（x 向右，y 向上），int / float 可混合。
- 多边形为顶点列表，**逆时针 (CCW) 为正方向**，`signed_area2` 为正。
- 凸包输出为 CCW 顶点列表，起点为字典序最小点，结果确定（与输入顺序无关）。

## 边界语义

- 所有线段均为**闭线段**：端点接触、共线重叠都算相交。
- `segment_intersection` 返回 `None` / `("point", p)` / `("segment", (a, b))`
  （共线重叠时给出公共子段，端点按坐标排序，结果确定）。
- `classify_point` 返回三态：`'inside'` / `'boundary'` / `'outside'`；
  边上的点（含顶点）一律为 `'boundary'`。
- `point_in_polygon(poly, p, include_boundary=True)` 默认边界算内部，
  可传 `include_boundary=False` 排除。
- 裁剪时凸裁剪窗口的边界是**闭的**：贴着裁剪边的边会被保留；
  输出顶点顺序稳定，跟随被裁剪多边形的环绕方向。

## 数值稳定性

- 全库统一使用 `geom2d.core.EPS = 1e-9` 这一个绝对容差，所有谓词
  （定向、共线、点在段上、裁剪内外判断）都经由同一组 `sign`/`cross`
  辅助函数，不存在不同算法判断互相矛盾的情况。
- **整数坐标模式**：当谓词涉及的所有坐标都是 `int` 时，使用精确整数
  算术（叉积为精确整数，与 0 比较，完全无浮点误差）。只有出现 float
  坐标时才启用 EPS 容差。因此整数输入下大坐标（如 1e9 量级）也不会
  误判共线。
- 测试中的交叉验证使用 `fractions.Fraction` 精确算术作为独立参照。

## 退化输入的确定行为

- 凸包：重复点自动去除；少于 3 个唯一点时返回排序后的唯一点；
  全部共线时返回两个端点（`include_collinear=True` 时保留边界上所有
  共线点，沿边界往返输出）。
- 多边形：空/单点/两点/共线多边形的面积为 0，方向为 `'degenerate'`。
- 裁剪：任一输入少于 3 个顶点时返回 `[]`；交集面积为 0 时返回 `[]`。

## 运行测试

```bash
cd <本目录>
python3 -m unittest discover -s tests -v
```

测试覆盖：共线/相交/端点接触的线段判定、凹多边形点包含、凸包（含
重复点、共线点、退化输入）、退化多边形、凸裁剪，以及基于独立暴力
算法（精确 Fraction 算术）的随机数据交叉验证（固定随机种子，可复现）。
