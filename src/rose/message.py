import time
import msgspec

# 元数据基础类型 (平替 ROS 的 std_msgs/Header)
class Header(msgspec.Struct):
    timestamp: float = msgspec.field(default_factory=time.time)  # 自动填入当前时间戳
    frame_id: str = ""  # 坐标系 ID，做 TF 变换和传感器融合时必备 (如 "base_link", "camera_rgb_optical_frame")

    @classmethod
    def from_dict(cls, header: dict) -> "Header":
        return cls(**header)

# 消息基类 (所有业务消息的父类)
class Message(msgspec.Struct, kw_only=True):  # kw_only True，解决继承时带默认值的字段顺序冲突问题
    header: Header = msgspec.field(default_factory=Header)  # 强制所有子类消息自带 header


# 几何/通用基础类型 (平替 geometry_msgs)
class Vector3(msgspec.Struct):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def to_tuple(self) -> tuple:
        return (self.x, self.y, self.z)
    
    @classmethod
    def from_tuple(cls, vec: tuple) -> "Vector3":
        return cls(*vec)

class Quaternion(msgspec.Struct):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 1.0  # 四元数实部默认为1

    def to_tuple(self) -> tuple:
        return (self.x, self.y, self.z, self.w)

    @classmethod
    def from_tuple(cls, quat: tuple) -> "Quaternion":
        return cls(*quat)

class Pose(msgspec.Struct):
    position: Vector3 = msgspec.field(default_factory=Vector3)
    orientation: Quaternion = msgspec.field(default_factory=Quaternion)
