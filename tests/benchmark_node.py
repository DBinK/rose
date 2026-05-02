"""Node 层通信性能基准测试

全部使用 Rose 的 `Publisher` / `Subscriber` / `Service` / `Client` API。

测试要点：
1. Pub/Sub 单向延迟（小消息 / 大消息）
2. RPC 调用延迟
3. Pub/Sub 吞吐量

注意：这些测试依赖 Zenoh 进程间通信，结果受系统负载影响。
"""

import queue
import socket
import time
from collections.abc import Generator

import pytest
import zenoh

from rose.message import Message
from rose.node import Client, Publisher, Service, Subscriber


# ---------- Rose 消息类型 ----------

class SmallMsg(Message):
    __test__ = False
    value: str


class LargeMsg(Message):
    __test__ = False
    data: list[float]


class AddReq(Message):
    __test__ = False
    a: int
    b: int


class AddRes(Message):
    __test__ = False
    sum: int


class TimedSmallMsg(Message):
    """带发送时间戳的小消息，用于 Pub/Sub 单向延迟测量"""
    __test__ = False
    payload: str
    send_timestamp_ns: int


class TimedLargeMsg(Message):
    """带发送时间戳的大消息，用于 Pub/Sub 单向延迟测量"""
    __test__ = False
    data: list[float]
    send_timestamp_ns: int


# ---------- 辅助函数 ----------

_SMALL_PAYLOAD_SIZE = 50  # bytes (约)
_LARGE_PAYLOAD_SIZE = 4096  # bytes (约 4KB)


@pytest.fixture(scope="module")
def paired_sessions() -> Generator[tuple[zenoh.Session, zenoh.Session], None, None]:
    """创建一对 TCP 连接的 Zenoh Session"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]

    cfg_a = zenoh.Config()
    cfg_a.insert_json5("listen/endpoints", f'["tcp/127.0.0.1:{port}"]')
    session_a = zenoh.open(cfg_a)

    cfg_b = zenoh.Config()
    cfg_b.insert_json5("connect/endpoints", f'["tcp/127.0.0.1:{port}"]')
    session_b = zenoh.open(cfg_b)

    time.sleep(0.5)
    yield session_a, session_b

    try:
        session_a.close()
    except Exception:
        pass
    try:
        session_b.close()
    except Exception:
        pass


# ---------- Pub/Sub 单向延迟 ----------

class TestPubSubLatency:
    """通过 Rose Publisher/Subscriber 测试 Pub/Sub 单向延迟"""

    def test_small_message_latency(self, benchmark, paired_sessions) -> None:
        """小消息 (50B) 单向延迟"""
        session_a, session_b = paired_sessions
        node_name = "bench"
        topic = "bench/latency/small"
        q: queue.Queue[float] = queue.Queue()

        def on_msg(msg: TimedSmallMsg, key: str) -> None:
            latency = (time.monotonic_ns() - msg.send_timestamp_ns) / 1000  # ns -> µs
            q.put(latency)

        Subscriber(session_b, node_name, topic, TimedSmallMsg, on_msg)
        time.sleep(0.3)
        pub = Publisher(session_a, node_name, topic, TimedSmallMsg)

        def _send_one() -> None:
            ts = time.monotonic_ns()
            pub.publish(TimedSmallMsg(payload="hello", send_timestamp_ns=ts))
            try:
                q.get(timeout=2.0)
            except queue.Empty:
                pytest.fail("超时：未收到消息")

        benchmark(_send_one)

    def test_large_message_latency(self, benchmark, paired_sessions) -> None:
        """大消息 (4KB) 单向延迟"""
        session_a, session_b = paired_sessions
        node_name = "bench"
        topic = "bench/latency/large"
        q: queue.Queue[float] = queue.Queue()

        def on_msg(msg: TimedLargeMsg, key: str) -> None:
            latency = (time.monotonic_ns() - msg.send_timestamp_ns) / 1000
            q.put(latency)

        Subscriber(session_b, node_name, topic, TimedLargeMsg, on_msg)
        time.sleep(0.3)
        pub = Publisher(session_a, node_name, topic, TimedLargeMsg)

        large_data = [float(i) for i in range(512)]

        def _send_one() -> None:
            ts = time.monotonic_ns()
            pub.publish(TimedLargeMsg(data=large_data, send_timestamp_ns=ts))
            try:
                q.get(timeout=2.0)
            except queue.Empty:
                pytest.fail("超时：未收到消息")

        benchmark(_send_one)


# ---------- Publisher 吞吐量 ----------

class TestPublisherThroughput:
    """通过 Rose Publisher/Subscriber 测试发布吞吐量"""

    @pytest.mark.skip(reason="需要人工验证")
    def test_publish_small_messages(self, benchmark, paired_sessions) -> None:
        """小消息 (50B) 发布吞吐量"""
        session_a, session_b = paired_sessions
        node_name = "bench"
        topic = "bench/small"

        Subscriber(session_b, node_name, topic, SmallMsg, lambda msg, key: None)
        time.sleep(0.3)

        pub = Publisher(session_a, node_name, topic, SmallMsg)
        msg = SmallMsg(value="hello")

        def _publish_batch() -> None:
            for _ in range(100):
                pub.publish(msg)

        benchmark(_publish_batch)


class TestRpcLatency:
    """RPC 调用延迟基准测试（已使用 Rose API）"""

    def test_rpc_roundtrip_latency(self, benchmark, node) -> None:
        def handle_add(req: AddReq) -> AddRes:
            return AddRes(sum=req.a + req.b)

        node.create_service("bench/add", AddReq, AddRes, handle_add)
        time.sleep(0.3)

        client = node.create_client("bench/add", AddReq, AddRes)
        client.wait_for_service(timeout=2.0)

        def _call() -> None:
            client.call(AddReq(a=10, b=20))

        benchmark(_call)
