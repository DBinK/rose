"""图像传输 Pub/Sub 性能基准测试

使用 Rose 的 `Publisher` / `Subscriber` API，测试大带宽场景下框架的实际性能。

测试要点：
1. 不同分辨率 JPEG 的传输吞吐量 (img/s) — 通过 Rose Publisher.publish() 批量发送
2. 图像传输单向延迟 — 通过 Rose Subscriber 回调 + 消息内时间戳测量
"""

import queue
import socket
import time
from collections.abc import Generator

import cv2
import numpy as np
import pytest
import zenoh

from rose.message import Message
from rose.node import Publisher, Subscriber


# ---------- Rose 消息类型 ----------

class ImageFrame(Message):
    """纯图像帧，用于吞吐量测试"""
    __test__ = False
    data: bytes


class TimedImageFrame(Message):
    """带时间戳的图像帧，用于延迟测试"""
    __test__ = False
    data: bytes
    send_timestamp_ns: int


# ---------- 预生成测试图像 ----------

def _gen_jpeg(w: int, h: int, quality: int = 85) -> bytes:
    img = np.random.randint(0, 256, (h, w, 3), dtype=np.uint8)
    success, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not success:
        raise RuntimeError("JPEG 编码失败")
    return buf.tobytes()


_JPEG_VGA = _gen_jpeg(640, 480)
_JPEG_HD = _gen_jpeg(1280, 720)
_JPEG_FHD = _gen_jpeg(1920, 1080)
_RAW_VGA = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8).tobytes()

# (name, data, batch_size) — batch_size 根据分辨率调整，保证单次测量耗时合理
_IMAGE_TABLE: list[tuple[str, bytes, int]] = [
    ("VGA JPEG",  _JPEG_VGA, 100),
    ("HD JPEG",   _JPEG_HD,   50),
    ("FHD JPEG",  _JPEG_FHD,  20),
    ("VGA RAW",   _RAW_VGA,   20),
]


@pytest.fixture(scope="module")
def img_sessions() -> Generator[tuple[zenoh.Session, zenoh.Session], None, None]:
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


# ---------- 吞吐量 ----------

class TestImageThroughput:
    """通过 Rose Publisher/Subscriber 测试图像吞吐量"""

    @pytest.mark.parametrize("name,data,batch_size", [
        pytest.param(n, d, b, id=n) for n, d, b in _IMAGE_TABLE
    ])
    def test_throughput(self, benchmark, img_sessions, name: str, data: bytes, batch_size: int) -> None:
        """批量发送图像，测量 Rose Publisher.publish() 吞吐量"""
        session_a, session_b = img_sessions
        node_name = "img_bench"
        topic = f"bench/img/throughput/{name.lower().replace(' ', '_')}"

        # Subscriber（回调模式，收包即弃）
        Subscriber(session_b, node_name, topic, ImageFrame, lambda msg, key: None)
        time.sleep(0.3)

        pub = Publisher(session_a, node_name, topic, ImageFrame)
        msg = ImageFrame(data=data)

        def _send_batch() -> None:
            for _ in range(batch_size):
                pub.publish(msg)

        benchmark(_send_batch)


# ---------- 延迟 ----------

class TestImageLatency:
    """通过 Rose 消息内时间戳测量图像单向延迟"""

    @pytest.mark.parametrize("name,data", [
        pytest.param(n, d, id=n) for n, d in [
            ("VGA JPEG", _JPEG_VGA),
            ("HD JPEG",  _JPEG_HD),
            ("FHD JPEG", _JPEG_FHD),
        ]
    ])
    def test_latency(self, benchmark, img_sessions, name: str, data: bytes) -> None:
        """单帧发送，通过 TimedImageFrame 内的 send_timestamp_ns 计算延迟"""
        session_a, session_b = img_sessions
        node_name = "img_bench"
        topic = f"bench/img/latency/{name.lower().replace(' ', '_')}"
        q: queue.Queue[float] = queue.Queue()

        def on_frame(msg: TimedImageFrame, key: str) -> None:
            latency = (time.monotonic_ns() - msg.send_timestamp_ns) / 1000  # ns -> µs
            q.put(latency)  # type: ignore[arg-type]

        Subscriber(session_b, node_name, topic, TimedImageFrame, on_frame)
        time.sleep(0.3)

        pub = Publisher(session_a, node_name, topic, TimedImageFrame)

        def _send_one() -> None:
            ts = time.monotonic_ns()
            pub.publish(TimedImageFrame(data=data, send_timestamp_ns=ts))
            try:
                q.get(timeout=5.0)
            except queue.Empty:
                pytest.fail("超时：未收到图像")

        benchmark(_send_one)
