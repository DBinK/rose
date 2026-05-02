"""Message 层纯单元测试

测试要点：
1. Struct 默认值 / 字段类型
2. msgspec msgpack 序列化与反序列化
3. Vector3 / Quaternion 工具方法 to_tuple / from_tuple
4. Pose 组合结构
"""

import math

import msgspec
import pytest

from rose.message import Header, Message, Pose, Quaternion, Vector3


class TestHeader:
    def test_default_timestamp(self) -> None:
        """Header 的 timestamp 应该自动填入当前时间戳（接近 realtime）"""
        h = Header()
        assert h.timestamp > 0
        assert h.frame_id == ""

    def test_custom_frame_id(self) -> None:
        h = Header(frame_id="base_link")
        assert h.frame_id == "base_link"

    def test_custom_timestamp(self) -> None:
        h = Header(timestamp=42.0, frame_id="map")
        assert h.timestamp == 42.0


class TestMessage:
    def test_default_header(self) -> None:
        """Message 应该自动附带一个 Header"""
        m = Message()
        assert isinstance(m.header, Header)
        assert m.header.timestamp > 0

    def test_custom_header(self) -> None:
        m = Message(header=Header(frame_id="odom"))
        assert m.header.frame_id == "odom"

    def test_subclass_with_fields(self) -> None:
        """子类消息可以添加业务字段"""

        class SensorData(Message):
            temperature: float
            humidity: float

        data = SensorData(temperature=25.5, humidity=60.0)
        assert data.temperature == 25.5
        assert data.humidity == 60.0
        assert isinstance(data.header, Header)


class TestSerialization:
    """msgspec msgpack 序列化/反序列化"""

    def test_roundtrip(self) -> None:
        class Pose2D(Message):
            x: float
            y: float
            theta: float

        encoder = msgspec.msgpack.Encoder()
        decoder = msgspec.msgpack.Decoder(Pose2D)

        original = Pose2D(x=1.0, y=2.0, theta=0.5)
        payload = encoder.encode(original)
        restored = decoder.decode(payload)

        assert restored.x == original.x
        assert restored.y == original.y
        assert restored.theta == original.theta

    def test_validation_error(self) -> None:
        """反序列化类型不匹配时应抛出 ValidationError"""

        class TempMsg(Message):
            value: int

        decoder = msgspec.msgpack.Decoder(TempMsg)
        bad_payload = msgspec.msgpack.Encoder().encode({"value": "not_an_int"})

        with pytest.raises(msgspec.ValidationError):
            decoder.decode(bad_payload)


class TestVector3:
    def test_default_values(self) -> None:
        v = Vector3()
        assert v.to_tuple() == (0.0, 0.0, 0.0)

    def test_custom_values(self) -> None:
        v = Vector3(x=1.0, y=2.0, z=3.0)
        assert v.to_tuple() == (1.0, 2.0, 3.0)

    def test_from_tuple(self) -> None:
        v = Vector3.from_tuple((4.0, 5.0, 6.0))
        assert v.x == 4.0
        assert v.y == 5.0
        assert v.z == 6.0


class TestQuaternion:
    def test_default_identity(self) -> None:
        """默认四元数应该是单位四元数 (w=1)"""
        q = Quaternion()
        assert q.to_tuple() == (0.0, 0.0, 0.0, 1.0)

    def test_from_tuple(self) -> None:
        q = Quaternion.from_tuple((0.0, 0.0, math.sin(math.pi / 4), math.cos(math.pi / 4)))
        assert pytest.approx(q.x) == 0.0
        assert pytest.approx(q.y) == 0.0
        assert pytest.approx(q.z) == math.sin(math.pi / 4)
        assert pytest.approx(q.w) == math.cos(math.pi / 4)


class TestPose:
    def test_default_values(self) -> None:
        pose = Pose()
        assert pose.position.to_tuple() == (0.0, 0.0, 0.0)
        assert pose.orientation.to_tuple() == (0.0, 0.0, 0.0, 1.0)

    def test_custom_position(self) -> None:
        pose = Pose(position=Vector3(x=1.0, y=2.0, z=3.0))
        assert pose.position.to_tuple() == (1.0, 2.0, 3.0)
