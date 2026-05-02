"""Message 层性能基准测试

测试要点：
1. 消息编码（msgpack serialize）吞吐量
2. 消息解码（msgpack deserialize）吞吐量
3. 大量字段消息的序列化性能
"""

import msgspec
import pytest

from rose.message import Header, Message, Pose, Quaternion, Vector3


# ---------- 基准测试辅助消息类型 ----------

class SmallMsg(Message):
    """小消息：少量标量字段"""
    temperature: float
    humidity: float


class MediumMsg(Message):
    """中等消息：组合类型"""
    pose: Pose
    velocity: Vector3


class LargeMsg(Message):
    """大消息：多个字段模拟传感器数据"""
    timestamp: float
    temperature: float
    humidity: float
    pressure: float
    altitude: float
    heading: float
    pitch: float
    roll: float
    linear_x: float
    linear_y: float
    linear_z: float
    angular_x: float
    angular_y: float
    angular_z: float


_small_encoder = msgspec.msgpack.Encoder()
_small_decoder = msgspec.msgpack.Decoder(SmallMsg)
_medium_encoder = msgspec.msgpack.Encoder()
_medium_decoder = msgspec.msgpack.Decoder(MediumMsg)
_large_encoder = msgspec.msgpack.Encoder()
_large_decoder = msgspec.msgpack.Decoder(LargeMsg)

_small_instance = SmallMsg(temperature=25.5, humidity=60.0)
_medium_instance = MediumMsg(
    pose=Pose(position=Vector3(1.0, 2.0, 3.0), orientation=Quaternion(0.0, 0.0, 0.707, 0.707)),
    velocity=Vector3(0.1, 0.0, 0.0),
)
_large_instance = LargeMsg(
    timestamp=1234567890.0,
    temperature=25.5,
    humidity=60.0,
    pressure=1013.25,
    altitude=100.0,
    heading=45.0,
    pitch=0.5,
    roll=0.1,
    linear_x=1.0,
    linear_y=0.0,
    linear_z=0.0,
    angular_x=0.0,
    angular_y=0.0,
    angular_z=0.0,
)
_small_payload = _small_encoder.encode(_small_instance)
_medium_payload = _medium_encoder.encode(_medium_instance)
_large_payload = _large_encoder.encode(_large_instance)


class TestMessageEncodeBenchmark:
    """消息编码性能"""

    def test_encode_small(self, benchmark) -> None:
        """小消息（2 个 float 字段）编码"""
        benchmark(_small_encoder.encode, _small_instance)

    def test_encode_medium(self, benchmark) -> None:
        """中等消息（Pose + Vector3 组合）编码"""
        benchmark(_medium_encoder.encode, _medium_instance)

    def test_encode_large(self, benchmark) -> None:
        """大消息（14 个字段）编码"""
        benchmark(_large_encoder.encode, _large_instance)


class TestMessageDecodeBenchmark:
    """消息解码性能"""

    def test_decode_small(self, benchmark) -> None:
        """小消息解码"""
        benchmark(_small_decoder.decode, _small_payload)

    def test_decode_medium(self, benchmark) -> None:
        """中等消息解码"""
        benchmark(_medium_decoder.decode, _medium_payload)

    def test_decode_large(self, benchmark) -> None:
        """大消息解码"""
        benchmark(_large_decoder.decode, _large_payload)


class TestMessageRoundtripBenchmark:
    """消息完整编解码往返（模拟真实发布/订阅链路）"""

    def test_small_roundtrip(self, benchmark) -> None:
        payload = _small_encoder.encode(_small_instance)
        benchmark(_small_decoder.decode, payload)

    def test_large_roundtrip(self, benchmark) -> None:
        payload = _large_encoder.encode(_large_instance)
        benchmark(_large_decoder.decode, payload)


class TestStructCreationBenchmark:
    """Struct 对象创建性能"""

    def test_create_small_message(self, benchmark) -> None:
        benchmark(SmallMsg, temperature=25.5, humidity=60.0)

    def test_create_header(self, benchmark) -> None:
        benchmark(Header)

    def test_create_vector3(self, benchmark) -> None:
        benchmark(Vector3, x=1.0, y=2.0, z=3.0)
