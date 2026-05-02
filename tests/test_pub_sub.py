"""Publisher ↔ Subscriber 基础集成测试

核心策略：
- 对无需跨 Session 的测试使用单个 Session（最稳定）
- 对需跨 Session 的测试使用 _paired_sessions() + 充裕等待
"""

import socket
import time

import zenoh


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


class TestPubSubSameSession:
    """同 Session 内发布订阅测试（最可靠的测试方式）"""

    def test_pub_sub_string(self) -> None:
        """发布字符串"""
        session = zenoh.open(zenoh.Config())
        time.sleep(0.3)

        received: list[str] = []
        sub = session.declare_subscriber("test/same/str", lambda s: received.append(s.payload.to_string()))

        pub = session.declare_publisher("test/same/str")
        pub.put(b"hello world")
        time.sleep(0.3)

        assert len(received) == 1
        assert received[0] == "hello world"

        _safe_close(session)

    def test_pub_sub_bytes(self) -> None:
        """发布二进制数据"""
        session = zenoh.open(zenoh.Config())
        time.sleep(0.3)

        received: list[bytes] = []
        sub = session.declare_subscriber("test/same/bytes", lambda s: received.append(s.payload.to_bytes()))

        pub = session.declare_publisher("test/same/bytes")
        pub.put(b"\x00\x01\x02\xff")
        time.sleep(0.3)

        assert len(received) == 1
        assert received[0] == b"\x00\x01\x02\xff"

        _safe_close(session)

    def test_multiple_messages(self) -> None:
        """连续发布多条"""
        session = zenoh.open(zenoh.Config())
        time.sleep(0.3)

        received: list[str] = []
        sub = session.declare_subscriber("test/same/multi", lambda s: received.append(s.payload.to_string()))

        pub = session.declare_publisher("test/same/multi")
        for i in range(5):
            pub.put(str(i).encode())
        time.sleep(0.3)

        assert len(received) == 5
        assert received == ["0", "1", "2", "3", "4"]

        _safe_close(session)

    def test_wildcard_sub(self) -> None:
        """通配符订阅"""
        session = zenoh.open(zenoh.Config())
        time.sleep(0.3)

        received: list[str] = []
        sub = session.declare_subscriber("sensor/**", lambda s: received.append(f"{s.key_expr}:{s.payload.to_string()}"))

        pub_a = session.declare_publisher("sensor/temp")
        pub_b = session.declare_publisher("sensor/humidity")
        pub_a.put(b"25.5")
        pub_b.put(b"60.0")
        time.sleep(0.3)

        assert len(received) == 2
        assert "sensor/temp:25.5" in received
        assert "sensor/humidity:60.0" in received

        _safe_close(session)

    def test_publish_without_subscriber(self) -> None:
        """没有订阅者时发布不应报错"""
        session = zenoh.open(zenoh.Config())
        time.sleep(0.3)
        pub = session.declare_publisher("test/same/no_sub")
        pub.put(b"this is fine")
        _safe_close(session)


class TestPubSubCrossSession:
    """跨 Session 发布订阅测试（验证真实网络通信能力）"""

    def test_pub_sub_string(self) -> None:
        session_a, session_b = _paired_sessions()

        received: list[str] = []
        sub = session_b.declare_subscriber("test/cross/str", lambda s: received.append(s.payload.to_string()))
        time.sleep(0.5)

        pub = session_a.declare_publisher("test/cross/str")
        pub.put(b"cross session hello")
        time.sleep(0.5)

        assert len(received) == 1
        assert received[0] == "cross session hello"

        sub.undeclare()
        pub.undeclare()
        session_b.close()
        session_a.close()
