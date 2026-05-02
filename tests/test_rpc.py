"""Service ↔ Client (RPC) 一对一集成测试

使用显式 TCP 端点连接的 Session 对。
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


class TestRpcBasic:
    """基础 RPC 测试"""

    def test_simple_request_reply(self) -> None:
        """发送请求并接收回复"""
        session_a, session_b = _paired_sessions()

        queryable = session_b.declare_queryable(
            "rpc/echo",
            lambda q: q.reply(q.key_expr, f"echo:{q.payload.to_string()}".encode()),
        )
        time.sleep(0.3)

        replies = session_a.get("rpc/echo", payload=b"hello", timeout=5.0)
        results = [r.ok.payload.to_string() for r in replies if r.ok]

        assert len(results) == 1
        assert results[0] == "echo:hello"

        queryable.undeclare()
        _safe_close(session_b, session_a)

    def test_multiple_requests(self) -> None:
        """连续多次 RPC 调用"""
        session_a, session_b = _paired_sessions()

        queryable = session_b.declare_queryable(
            "rpc/double",
            lambda q: q.reply(q.key_expr, str(int(q.payload.to_string()) * 2).encode()),
        )
        time.sleep(0.3)

        for val in [1, 2, 3]:
            replies = session_a.get("rpc/double", payload=str(val).encode(), timeout=5.0)
            results = [r.ok.payload.to_string() for r in replies if r.ok]
            assert len(results) == 1
            assert results[0] == str(val * 2)

        queryable.undeclare()
        _safe_close(session_b, session_a)


class TestRpcErrorHandling:
    """RPC 错误处理测试"""

    def test_service_returns_error(self) -> None:
        """服务端返回 reply_err"""
        session_a, session_b = _paired_sessions()

        queryable = session_b.declare_queryable(
            "rpc/error",
            lambda q: q.reply_err(b"internal error"),
        )
        time.sleep(0.3)

        replies = session_a.get("rpc/error", payload=b"data", timeout=5.0)
        errors = [r.err.payload.to_string() for r in replies if r.err is not None]

        assert len(errors) == 1
        assert "internal error" in errors[0]

        queryable.undeclare()
        _safe_close(session_b, session_a)

    def test_no_service_timeout(self) -> None:
        """没有服务端时应超时返回空"""
        session = zenoh.open(zenoh.Config())
        time.sleep(0.3)
        replies = list(session.get("rpc/nobody", payload=b"data", timeout=0.5))
        assert len(replies) == 0
        session.close()
