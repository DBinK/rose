<p align="center">
  <a href="https://zread.ai/DBinK/rose" target="_blank"><img src="https://img.shields.io/badge/Ask_Zread-_.svg?style=flat&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff" alt="zread"/></a>

  <!-- PyPI -->
  <a href="https://pypi.org/project/rose/">
    <img src="https://img.shields.io/pypi/v/rose?color=blue&label=PyPI&logo=pypi&logoColor=white" />
  </a>

  <!-- License -->
  <a href="https://github.com/DBinK/rose/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/DBinK/rose?color=blue" />
  </a>

  <!-- CI -->
  <a href="https://github.com/DBinK/rose/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/DBinK/rose/test_and_publish.yml?branch=main&logo=githubactions&logoColor=white" />
  </a>


  <!-- Last Commit -->
  <a href="https://github.com/DBinK/rose/commits/main">
    <img src="https://img.shields.io/github/last-commit/DBinK/rose" />
  </a>

  <!-- Stars -->
  <a href="https://github.com/DBinK/rose">
    <img src="https://img.shields.io/github/stars/DBinK/rose?style=social" />
  </a>

</p>

<div align="center">
  <!-- Keep these links. Translations will automatically update with the README. -->
  <a href="https://www.zdoc.app/DBinK/rose?lang=en">English</a> | 
  <a href="https://www.zdoc.app/DBinK/rose?lang=ja">日本語</a> | 
  <a href="https://www.zdoc.app/DBinK/rose?lang=de">Deutsch</a> | 
  <a href="https://www.zdoc.app/DBinK/rose?lang=es">Español</a> | 
  <a href="https://www.zdoc.app/DBinK/rose?lang=fr">français</a> | 
  <a href="https://www.zdoc.app/DBinK/rose?lang=ko">한국어</a> | 
  <a href="https://www.zdoc.app/DBinK/rose?lang=pt">Português</a> | 
  <a href="https://www.zdoc.app/DBinK/rose?lang=ru">Русский</a>
</div>

# Rose 🌹

一个基于 [Zenoh](https://zenoh.io/) 构建的轻量级、类似 ROS2 的机器人通信框架。

## 设计理念

Rose 是一个极简的发布/订阅与 RPC 通信框架，借鉴 ROS2 的节点（Node）、话题（Topic）、服务（Service）概念，但底层通信完全基于 **Zenoh**，不依赖 DDS 栈。

核心特点：

- **轻量**: 核心依赖仅包含 `zenoh`、`msgspec` ，无 DDS、无 ROS 生态包袱 (`typer`/`loguru`/`rich` 仅调试用途)
- **类型安全**: 基于 `msgspec.Struct` 定义消息，自动 msgpack 序列化，编译时（IDE）和运行时双重类型校验
- **声明式风格**: 通过 `Node` 工厂方法创建发布者/订阅者/服务/客户端，API 清晰一致
- **自发现拓扑**: 利用 Zenoh Liveliness Token 实现节点/话题/服务的自动发现，并提供 `rrr` CLI 工具查看网络拓扑

## 安装

```bash
pip install rose-py
```

或者使用 `uv`：

```bash
uv add rose-py
```

## 快速入门

### 发布/订阅模式

**1. 定义消息**

```python
# msg.py
from rose import Message


class EnvSensorData(Message):
    """环境传感器数据"""
    temperature: float
    humidity: float
```

**2. 发布者**

```python
# pub.py
import time
from loguru import logger
from rose import Node

from msg import EnvSensorData

node = Node("sensor_hub_1")
pub = node.create_publisher("room_a/sensor/env", EnvSensorData)

logger.success("传感器节点启动，开始广播数据...")

try:
    temp = 25.0
    while True:
        msg = EnvSensorData(
            # header={"frame_id": "sensor_link_1"},  # 可选覆盖
            temperature=temp,
            humidity=60.5,
        )
        pub.publish(msg)
        logger.info(f"已发送 -> 温度: {msg.temperature}°C")
        temp += 0.001
        time.sleep(0.1)

except KeyboardInterrupt:
    node.close()
```

**3. 订阅者（回调模式）**

```python
# sub_callback.py
from loguru import logger
from rich import print as rprint
from rose import Node

from msg import EnvSensorData

node = Node("data_logger")


def on_sensor_data(msg: EnvSensorData, source_key: str) -> None:
    logger.success(f"收到来自 [{source_key}] 的数据:")
    rprint(msg)


node.create_subscriber("room_a/sensor/env", EnvSensorData, on_sensor_data)

logger.success("日志节点已就绪，正在监听传感器网络...")
node.spin()
```

**4. 订阅者（轮询模式）**

```python
# sub_polling.py
from loguru import logger
from rich import print as rprint
from rose import Node

from msg import EnvSensorData

node = Node("data_logger")
sub = node.create_subscriber("room_a/sensor/env", EnvSensorData)

try:
    while True:
        msg, key = sub.recv()
        logger.success(f"收到 [{key}]:")
        rprint(msg)
except KeyboardInterrupt:
    node.close()
```

### RPC 模式（服务/客户端）

**1. 定义消息**

```python
# msg.py
from rose import Message


class AddIntsReq(Message):
    a: int
    b: int


class AddIntsRes(Message):
    sum: int


class DivFloatsReq(Message):
    a: float
    b: float


class DivFloatsRes(Message):
    quotient: float
```

**2. 服务端**

```python
# server.py
from loguru import logger
from rose import Node

from msg import AddIntsReq, AddIntsRes, DivFloatsReq, DivFloatsRes


def handle_add(req: AddIntsReq) -> AddIntsRes:
    logger.info(f"服务端收到计算请求: {req.a} + {req.b}")
    return AddIntsRes(sum=req.a + req.b)


def handle_div(req: DivFloatsReq) -> DivFloatsRes:
    logger.info(f"服务端收到计算请求: {req.a} / {req.b}")
    return DivFloatsRes(quotient=req.a / req.b)


node = Node("math_server")
node.create_service("math/add", AddIntsReq, AddIntsRes, handle_add)
node.create_service("math/div", DivFloatsReq, DivFloatsRes, handle_div)

logger.success("加法和除法服务已就绪，等待客户端调用...")
node.spin()
```

**3. 客户端**

```python
# client.py
from rich import print as rprint
from rose import Node

from msg import AddIntsReq, AddIntsRes, DivFloatsReq, DivFloatsRes

node = Node("math_client")

# 加法
add_client = node.create_client("math/add", AddIntsReq, AddIntsRes)
if not add_client.wait_for_service(timeout=3):
    print("服务端未就绪，请稍后再试")
    exit(1)

res = add_client.call(AddIntsReq(a=10, b=20))
rprint(res)

# 除法
div_client = node.create_client("math/div", DivFloatsReq, DivFloatsRes)
res = div_client.call(DivFloatsReq(a=10.0, b=2.0))
rprint(res)
```

## API 概览

### `Node`

节点是通信的核心容器，每个 Node 内部维护一个 Zenoh Session。

| 方法 | 描述 |
|------|------|
| `Node(name)` | 创建节点，自动建立 Zenoh 会话 |
| `node.spin()` | 保持节点运行，直到 `Ctrl+C` |
| `node.close()` | 优雅关闭节点，释放资源 |

支持 `with` 语句自动管理生命周期：

```python
with Node("my_node") as node:
    # 做点什么
    pass  # 自动 close()
```

### `Message`

所有消息的基类，继承 `msgspec.Struct`，自带 `Header` 字段：

- `header.timestamp` — 自动填入当前时间戳
- `header.frame_id` — 坐标系 ID（如 `"base_link"`）

子类只需添加业务字段：

```python
class MyMsg(Message):
    value: float
```

### `Publisher[MsgType]`

```python
pub = node.create_publisher(key_expr, MsgClass)
pub.publish(msg)
```

- 发布时自动做类型校验，类型不匹配抛出 `TypeError`
- 自动注册 Liveliness Token

### `Subscriber[MsgType]`

```python
# 回调模式
sub = node.create_subscriber(key_expr, MsgClass, callback)

# 轮询模式
sub = node.create_subscriber(key_expr, MsgClass)
msg, key = sub.recv(timeout=2.0)
```

### `Service[ReqType, ResType]`

```python
service = node.create_service(key_expr, ReqClass, ResClass, handler)
```

- `handler` 接收请求消息，返回响应消息
- 异常自动捕获并返回错误信息给客户端

### `Client[ReqType, ResType]`

```python
client = node.create_client(key_expr, ReqClass, ResClass)
if client.wait_for_service(timeout=3):
    res = client.call(request, timeout=2.0)
```

- `wait_for_service()` — 通过 Liveliness Token 探测服务端
- `call()` — 同步阻塞调用，超时抛出 `TimeoutError`

### 内置基础类型

Rose 内置了一些类 ROS 的几何基础类型：

| 类型 | 说明 |
|------|------|
| `Vector3` | 三维向量 `(x, y, z)`，提供 `to_tuple()` / `from_tuple()` |
| `Quaternion` | 四元数 `(x, y, z, w)`，默认单位四元数 `w=1` |
| `Pose` | 位姿，组合 `position: Vector3` 和 `orientation: Quaternion` |

## CLI 诊断工具

Rose 提供了一个 CLI 工具 `rrr`（Rose 网络诊断），用于查看当前网络的拓扑结构：

```bash
# 查看所有节点/话题/服务（完整拓扑）
rrr ls

# 列出所有节点
rrr node list

# 查看节点详情
rrr node info sensor_hub_1

# 列出所有话题
rrr topic list

# 查看话题详情
rrr topic info room_a/sensor/env

# 列出所有服务
rrr service list

# 查看服务详情
rrr service info math/add
```

## 项目结构

```
src/rose/
├── __init__.py     # 导出 Node, Message
├── message.py      # 消息基类 + 几何基础类型
├── node.py         # Node + Publisher/Subscriber/Service/Client
└── probe.py        # CLI 诊断工具
```

## 依赖

- `eclipse-zenoh >= 1.9.0`
- `msgspec >= 0.21.1`
- `typer >= 0.25.1`
- `loguru >= 0.7.3`
- `rich >= 15.0.0`

## 性能基准

以下基准测试在 `Windows 24H2` + `Python 3.13` 环境下运行，基于 `pytest-benchmark` 采集。

### 消息序列化（msgspec msgpack）

| 测试 | 平均耗时 | 说明 |
|------|---------|------|
| `Vector3` 创建 | **206 ns** | 3 字段 struct |
| `Header` 创建 | **274 ns** | 含 `time.time()` 默认值 |
| 小消息编码 (2字段) | **356 ns** | 例如 `EnvSensorData` |
| 小消息创建 | **457 ns** | struct 对象分配 |
| 小消息完整往返 | **495 ns** | 编码→解码全链路 |
| 小消息解码 | **619 ns** | 2 字段 msgpack 反序列化 |
| 大消息编码 (14字段) | **643 ns** | 模拟多传感器数据 |
| 中等消息编码 (组合) | **747 ns** | Pose + Vector3 嵌套 |
| 大消息解码 | **922 ns** | 14 字段反序列化 |
| 大消息完整往返 | **942 ns** | 编码→解码全链路 |
| 中等消息解码 | **1,052 ns** | 组合类型反序列化 |

> 消息序列化采用 `msgspec` msgpack 格式，性能接近 C 扩展级别，所有测试均达到 **百万级 OPS**。

### Pub/Sub 单向延迟

| 测试 | 平均耗时 | 中位数 | OPS |
|------|---------|--------|-----|
| 小消息单向 (50B) | **94.9 µs** | 87.5 µs | 10,538 ops/s |
| 大消息单向 (4KB) | **129.6 µs** | 114.0 µs | 7,713 ops/s |

> 单向延迟测量从 `pub.put()` 到 subscriber 回调执行之间的 `time.monotonic_ns()` 差值，包含 msgpack 编码/解码 + Zenoh TCP 传输全链路。同一进程内通过 TCP 回环连接。

### RPC 调用延迟

| 测试 | 平均耗时 | 中位数 | OPS |
|------|---------|--------|-----|
| RPC 往返调用 (Add) | **33.9 µs** | 27.0 µs | 29,458 ops/s |

> RPC 测试在同一进程内通过 Zenoh TCP 回环通信，包含 序列化 → Zenoh Put → 反序列化 → 处理 → 序列化 → 响应 的完整链路。

### 与 ROS 2 对比

| 维度 | Rose 🌹 | ROS 2 (Python rclpy) | 差距 |
|------|--------|----------------------|------|
| 消息编码 (2字段) | **356 ns** | ~1-3 µs¹ | **3-10x** 快 |
| 消息解码 (2字段) | **619 ns** | ~1-3 µs¹ | **3-5x** 快 |
| Pub/Sub 单向 (50B) | **94.9 µs** | ~300-2000 µs² | **5-20x** 快 |
| Pub/Sub 单向 (4KB) | **129.6 µs** | ~500-5000 µs² | **5-40x** 快 |
| RPC 往返调用 | **33.9 µs** | ~500-3000 µs² | **15-90x** 快 |

> ¹ ROS 2 序列化基于 Fast CDR（C++ 实现），但 Python 节点经过 `rclpy` → `rcl` → DDS 多层调用栈，实际开销远高于裸 CDR。
> ² ROS 2 Python 节点典型延迟范围，来源 [ROS 2 官方性能测试工具](https://docs.ros.org/en/iron/p/performance_test/) 及社区基准数据。

**差距来源分析：**

- **架构差异**：ROS 2 的 DDS 栈包含服务发现、QoS 协商、心跳维持等机制，这些在 Zenoh 中原生更轻量
- **调用层级**：`rclpy` → `rcl` → `DDS` 三层 vs **Rose** → **Zenoh** 两层，每层都有数据拷贝和上下文切换开销
- **序列化协议**：msgpack 比 CDR 更紧凑，解码无需查 schema，msgspec 的内存布局直接映射可零拷贝访问

**性能优化空间：**

当前延迟与原生 Zenoh C API（~5-10 µs）之间还有约 **85 µs** 的差距，主要来自 Python API 绑定和对象生命周期管理的开销。如果对极致性能有需求，可通过 Cython/Rust 封装关键路径进一步缩小差距。但对大多数机器人应用（控制周期通常 1-100 ms），当前水平已经绰绰有余。

### 运行基准测试

```bash
# 安装依赖
uv sync

# 消息序列化基准（无需 Zenoh 网络）
uv run pytest tests/benchmark_message.py --benchmark-only

# Node 层基准（Pub/Sub + RPC，需要 Zenoh TCP 连接）
uv run pytest tests/benchmark_node.py --benchmark-only

# 仅运行延迟测试（跳过吞吐量等需要人工验证的项）
uv run pytest tests/benchmark_node.py -k "latency or rpc" --benchmark-only
```

## License

MIT
