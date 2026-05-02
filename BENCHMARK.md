# 性能基准测试

> ⚠️ **免责声明**
>
> 本文档中的性能数据**仅供参考，不构成严谨的基准测试声明**。所有 Rose 数据均来自本地运行的 `pytest-benchmark`，ROS 2 对比数据来自公开的学术论文、技术报告及社区基准工具，测试环境、负载特征、QoS 配置均存在差异。**跨框架对比存在固有偏差**，不同测试平台、DDS 实现、消息规格下的结果可能显著不同。请结合实际场景评估。

---

## 测试环境

- **操作系统：** Windows 24H2
- **运行时：** Python 3.13
- **处理器：** AMD Ryzen 5 5600G (6C12T, 3.9 GHz)
- **内存：** 32 GB
- **通信链路：** Zenoh TCP 回环 (127.0.0.1)

---

## 消息序列化（msgspec msgpack）

| 测试 | 平均耗时 | 说明 |
|------|---------|------|
| `Header` 创建 | **127 ns** | 含 `time.time()` 默认值 |
| `Vector3` 创建 | **179 ns** | 3 字段 struct |
| 小消息创建 | **249 ns** | struct 对象分配 |
| 小消息完整往返 | **262 ns** | 编码→解码全链路 |
| 小消息编码 (2字段) | **307 ns** | 例如 `EnvSensorData` |
| 小消息解码 | **362 ns** | 2 字段 msgpack 反序列化 |
| 大消息编码 (14字段) | **413 ns** | 模拟多传感器数据 |
| 中等消息编码 (组合) | **528 ns** | Pose + Vector3 嵌套 |
| 大消息完整往返 | **535 ns** | 编码→解码全链路 |
| 大消息解码 | **639 ns** | 14 字段反序列化 |
| 中等消息解码 | **850 ns** | 组合类型反序列化 |

> 消息序列化采用 `msgspec` msgpack 格式，性能接近 C 扩展级别，所有测试均达到 **百万级 OPS**。

---

## 节点通信

### Pub/Sub 单向延迟

| 测试 | 平均耗时 | 中位数 | 最小值 | 最大值 | OPS |
|------|---------|--------|--------|--------|-----|
| 小消息单向 (50B) | **88.8 µs** | 78.0 µs | 65.5 µs | 839 µs | 11,266 ops/s |
| 大消息单向 (4KB) | **140.8 µs** | 132.0 µs | 92.2 µs | 4,730 µs | 7,100 ops/s |

> 单向延迟测量从 `Publisher.publish()` 到 Subscriber 回调执行之间的 `time.monotonic_ns()` 差值，覆盖 msgspec 编码/解码 + 类型校验 + Zenoh TCP 传输全链路。同一进程内通过 TCP 回环连接。

### RPC 调用延迟

| 测试 | 平均耗时 | 中位数 | 最小值 | 最大值 | OPS |
|------|---------|--------|--------|--------|-----|
| RPC 往返调用 (Add) | **30.8 µs** | 25.2 µs | 19.0 µs | 423 µs | 32,462 ops/s |

> RPC 测试在同一进程内通过 Zenoh TCP 回环通信，包含 序列化 → Zenoh Put → 反序列化 → 处理 → 序列化 → 响应 的完整链路。

---

## 图像传输

通过 OpenCV 生成随机图像，使用 Rose 的 `Publisher.publish()` / `Subscriber` 回调模式传输 `ImageFrame(Message)`，覆盖 msgspec 编码/解码 + Zenoh 传输全链路。

| 测试 | 单帧大小 | 平均 | 中位数 | 最小值 | 最大值 | 吞吐量 |
|------|---------|------|--------|--------|--------|--------|
| 640×480 JPEG | **227.5 KB** | 171 µs | 153 µs | 115 µs | 708 µs | **9,659 img/s** |
| 1280×720 JPEG | **680.4 KB** | 1,066 µs | 1,003 µs | 673 µs | 2,392 µs | **842 img/s** |
| 1920×1080 JPEG | **1,533.1 KB** | 3,466 µs | 3,416 µs | 2,432 µs | 6,630 µs | **317 img/s** |
| 640×480 RAW (RGB) | **900.0 KB** | — | — | — | — | **588 img/s** |

> RAW 吞吐量显著低于 JPEG（588 vs 9,659 img/s），因为 msgspec 对 900KB `bytes` 字段的编码开销远大于 227KB。实际场景建议用 JPEG 等压缩格式传输图像。

---

## 与 ROS 2 对比

> ⚠️ **以下对比不构成严谨的 Benchmark。** Rose 数据为本地运行结果，ROS 2 数据来自学术文献/社区基准（详见脚注），两个框架的测试平台、消息类型、QoS 配置均不相同。**请勿将此处数据用作产品选型的唯一依据。**

| 维度 | Rose 🌹 | ROS 2 (rclcpp C++) | 差距 |
|------|--------|-------------------|------|
| 消息编码 (2字段) | **0.307 µs** | ~0.05-0.1 µs¹ | C++ 快 **3-6x** |
| 消息解码 (2字段) | **0.362 µs** | ~0.05-0.1 µs¹ | C++ 快 **3-6x** |
| Pub/Sub 单向 (50B) | **88.8 µs** | ~50-200 µs² | **~持平** |
| Pub/Sub 单向 (4KB) | **140.8 µs** | ~100-500 µs² | **1-4x** 快 |
| RPC 往返调用 | **30.8 µs** | ~100-500 µs² | **3-16x** 快 |
| 640×480 JPEG 传输 | **171 µs** | ~2000-5000 µs³ | **12-29x** 快 |
| 1280×720 JPEG 传输 | **1,066 µs** | ~5000-15000 µs³ | **5-14x** 快 |
| 1920×1080 JPEG 传输 | **3,466 µs** | ~10000-30000 µs³ | **3-9x** 快 |

> ¹ Fast CDR（C++ 实现）裸序列化，纯 C 库直接内存操作。Rose 用 Python msgspec，编码慢 3-6x 在预期内。<br>
> ² ROS 2 C++ 节点（`rclcpp`）典型延迟范围，来源 ROS 2 官方 [performance_test](https://github.com/ros2/performance_test) 及 UW-Madison 技术报告 [TR-2023-03](https://sbel.wisc.edu/wp-content/uploads/sites/569/2023/04/TR-2023-03.pdf)。<br>
> ³ ROS 2 `image_transport/compressed`（C++）包含 OpenCV JPEG 编解码 + CDR 序列化 + DDS 分片。NVIDIA [ros2_benchmark](https://discourse.openrobotics.org/t/ros-2-benchmark-open-source-release/30753) 在 Jetson AGX Orin 上测 quarter HD (960×540) 全链路 ~14.5 ms，FHD 下叠加 DDS 分片，落在 10-30 ms 区间。<br>

<p align="center">
  <img src="https://github.com/user-attachments/assets/f098cd01-f07c-4327-9f13-0e53113c1739" style="width: 99%; height: auto;">
  <a>与 ROS 2 Humble 的延迟进行对比 (单位:µs) (仅供参考)</a>
</p>

### 差距来源分析

- **架构差异**：ROS 2 的 DDS 栈包含服务发现、QoS 协商、心跳维持等机制，这些在 Zenoh 中原生更轻量
- **调用层级**：`rclcpp` → `rcl` → `rmw` → `DDS` 四层 vs **Rose** → **Zenoh** 两层，每层都有数据拷贝和上下文切换开销
- **序列化协议**：msgpack 比 CDR 更紧凑，解码无需查 schema，msgspec 的内存布局直接映射可零拷贝访问
- **图像分片**：DDS 将大消息拆为 64KB 的 RTPS 分片，接收端重组，大图像下加剧延迟；Zenoh 的分段传输更简洁高效

### 性能优化空间

当前延迟与原生 Zenoh C API（~5-10 µs）之间还有约 **85 µs** 的差距，主要来自 Python API 绑定和对象生命周期管理的开销。如果对极致性能有需求，可通过 Cython/Rust 封装关键路径进一步缩小差距。但对大多数机器人应用（控制周期通常 1-100 ms，视频帧间隔 16-33 ms），当前水平已经绰绰有余。

---

## 运行基准测试

```bash
# 安装依赖
uv sync

# 消息序列化基准（无需 Zenoh 网络）
uv run pytest tests/benchmark_message.py --benchmark-only

# Node 层基准（Pub/Sub + RPC，需要 Zenoh TCP 连接）
uv run pytest tests/benchmark_node.py --benchmark-only

# 图像传输基准（需要 OpenCV，安装后自动可用）
uv run pytest tests/benchmark_image.py --benchmark-only

# 仅运行延迟测试（跳过吞吐量等需要人工验证的项）
uv run pytest tests/benchmark_node.py -k "latency or rpc" --benchmark-only
```
