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

## License

MIT
