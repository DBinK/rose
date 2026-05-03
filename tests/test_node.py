"""Node 生命周期和 Publisher/Subscriber/Client/Service 封装测试"""

import socket
import time

import msgspec
import pytest
import zenoh

from rose import Message, Node
from rose.node import Publisher, Subscriber


def _paired_sessions() -> tuple[zenoh.Session, zenoh.Session]:
    """创建一对 Session：一个监听，一个连接"""
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
    return session_a, session_b


def _safe_close(*sessions: zenoh.Session) -> None:
    for s in sessions:
        try:
            s.close()
        except Exception:
            pass


# ---------- 测试用的 Message 子类 ----------

class TestMsg(Message):
    __test__ = False
    value: str


class AddReq(Message):
    __test__ = False
    a: int
    b: int


class AddRes(Message):
    __test__ = False
    sum: int


_encoder = msgspec.msgpack.Encoder()
_decoder_test = msgspec.msgpack.Decoder(TestMsg)


# ---------- 测试开始 ----------

class TestNodeLifecycle:
    """Node 创建/关闭测试"""

    def test_create_and_close(self) -> None:
        node = Node("lifecycle_test")
        assert node.name == "lifecycle_test"
        assert not node._closed
        node.close()
        assert node._closed

    def test_context_manager(self) -> None:
        with Node("ctx_test") as node:
            assert not node._closed
        assert node._closed

    def test_double_close(self) -> None:
        """重复 close() 不应报错"""
        node = Node("double_close_test")
        node.close()
        node.close()


class TestPublisher:
    """Publisher 封装测试"""

    def test_publish_custom_message(self) -> None:
        """通过 Publisher 发送 msgpack 编码消息"""
        session_a, session_b = _paired_sessions()

        received: list[bytes] = []
        sub = session_b.declare_subscriber("test/pub/msg", lambda s: received.append(s.payload.to_bytes()))
        time.sleep(0.3)

        pub = Publisher(session_a, "test_node", "test/pub/msg", TestMsg)
        pub.publish(TestMsg(value="hello"))
        time.sleep(0.5)

        assert len(received) == 1
        decoded = _decoder_test.decode(received[0])
        assert decoded.value == "hello"

        sub.undeclare()
        _safe_close(session_b, session_a)

    def test_publish_wrong_type(self) -> None:
        """发布不匹配的类型应抛出 TypeError"""
        class OtherMsg(Message):
            __test__ = False
            x: int

        session_a, session_b = _paired_sessions()
        pub = Publisher(session_a, "test_node", "test/pub/wrong", TestMsg)
        try:
            with pytest.raises(TypeError, match="发布的消息类型必须是"):
                pub.publish(OtherMsg(x=42))  # type: ignore[arg-type]
        finally:
            _safe_close(session_b, session_a)


class TestSubscriber:
    """Subscriber 封装测试"""

    def test_callback_mode(self) -> None:
        """回调模式订阅"""
        session_a, session_b = _paired_sessions()

        received: list[str] = []

        def on_msg(msg: TestMsg, key: str) -> None:
            received.append(msg.value)

        Subscriber(session_b, "test_node", "test/sub/cb", TestMsg, on_msg)
        time.sleep(0.3)

        pub = session_a.declare_publisher("test/sub/cb")
        payload = _encoder.encode(TestMsg(value="callback_works"))
        pub.put(payload)
        time.sleep(0.5)

        assert len(received) == 1
        assert received[0] == "callback_works"

        _safe_close(session_b, session_a)

    def test_polling_mode(self) -> None:
        """轮询模式订阅 - recv() 返回消息"""
        session_a, session_b = _paired_sessions()

        sub = Subscriber(session_b, "test_node", "test/sub/poll", TestMsg)
        time.sleep(0.3)

        pub = session_a.declare_publisher("test/sub/poll")
        payload = _encoder.encode(TestMsg(value="poll_works"))
        pub.put(payload)
        time.sleep(0.5)

        msg = sub.recv(timeout=2.0)
        assert msg is not None
        assert msg.value == "poll_works"

        _safe_close(session_b, session_a)

    def test_recv_on_callback_mode(self) -> None:
        """回调模式下调 recv() 应抛出 RuntimeError"""
        session_a, session_b = _paired_sessions()
        sub = Subscriber(session_b, "test_node", "test/sub/err", TestMsg, lambda m, k: None)
        with pytest.raises(RuntimeError, match="不支持 recv"):
            sub.recv()
        _safe_close(session_b, session_a)

    def test_poll_timeout(self) -> None:
        """轮询超时应返回 None"""
        session_a, session_b = _paired_sessions()
        sub = Subscriber(session_b, "test_node", "test/sub/timeout", TestMsg)
        msg = sub.recv(timeout=0.3)
        assert msg is None
        _safe_close(session_b, session_a)


class TestServiceAndClient:
    """Service/Client 封装测试"""

    def test_rpc_roundtrip(self, node: Node) -> None:
        """Service + Client 完整 RPC 调用（同一 Node 内）"""
        def handle_add(req: AddReq) -> AddRes:
            return AddRes(sum=req.a + req.b)

        node.create_service("test/add", AddReq, AddRes, handle_add)
        time.sleep(0.3)

        client = node.create_client("test/add", AddReq, AddRes)
        ready = client.wait_for_service(timeout=2.0)
        assert ready, "服务未就绪"

        res = client.call(AddReq(a=10, b=20))
        assert res.sum == 30

    def test_wait_for_service_timeout(self, node: Node) -> None:
        """等待不存在的服务应超时返回 False"""
        client = node.create_client("test/nonexistent", AddReq, AddRes)
        ready = client.wait_for_service(timeout=0.5)
        assert not ready

    def test_call_timeout(self, node: Node) -> None:
        """调用不存在的服务应抛出 TimeoutError"""
        client = node.create_client("test/no_server", AddReq, AddRes)
        with pytest.raises(TimeoutError, match="超时"):
            client.call(AddReq(a=1, b=2), timeout=0.5)
