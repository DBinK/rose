
import time 
import msgspec
import zenoh
from loguru import logger
from typing import TypeVar, Callable, Generic

# 定义泛型，约束消息类型必须是 msgspec.Struct 的子类
MsgType = TypeVar("MsgType", bound=msgspec.Struct)

class Publisher(Generic[MsgType]):
    def __init__(self, session: zenoh.Session, key_expr: str):
        self._pub = session.declare_publisher(key_expr)
        self.encoder = msgspec.msgpack.encode
    
    def publish(self, msg: MsgType) -> None:
        payload = self.encoder(msg)  # 底层自动完成 msgpack 高速序列化
        self._pub.put(payload)


class Subscriber(Generic[MsgType]):
    def __init__(
        self, 
        session: zenoh.Session, 
        key_expr: str, 
        msg_class: type[MsgType], 
        callback: Callable[[MsgType, str], None] | None = None
    ):
        self._msg_class = msg_class
        self._callback = callback
        self._key_expr = key_expr
        self.decoder = msgspec.msgpack.decode
        
        if callback is not None:  # === 回调模式 ===
          
            def _zenoh_listener(sample: zenoh.Sample) -> None:
                try:
                    decoded_msg = self.decoder(sample.payload.to_bytes(), type=self._msg_class)
                    self._callback(decoded_msg, sample.key_expr)
                except msgspec.ValidationError as e:
                    logger.error(f"key_expr '{key_expr}' 消息解析失败: {e}")
            self._sub = session.declare_subscriber(key_expr, _zenoh_listener)
        else:  # === 阻塞接收模式：不传 callback，Subscriber 自带 recv() ===
            self._sub = session.declare_subscriber(key_expr)

    def recv(self, timeout: float | None = None) -> tuple[MsgType, str] | None:
        """阻塞接收一条消息。"""
        if self._callback is not None:
            raise RuntimeError("该 Subscriber 使用回调模式，不支持 recv()")

        if timeout is None:
            # 无限阻塞
            sample = self._sub.recv()
        else:
            # 带超时的轮询
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                sample = self._sub.try_recv()
                if sample is not None:
                    break
                time.sleep(0.001)
            else:
                return None

        decoded = self.decoder(sample.payload.to_bytes(), type=self._msg_class)
        return decoded, sample.key_expr

class Node:
    def __init__(self, name: str):
        self.name = name
        self.session = zenoh.open(zenoh.Config())  # 初始化通信引擎，默认自动多播发现
        logger.info(f"Node '{self.name}' 已启动")

    def create_publisher(self, key_expr: str, msg_class: type[MsgType]) -> Publisher[MsgType]:
        return Publisher(self.session, key_expr)

    def create_subscriber(
        self, 
        key_expr: str, 
        msg_class: type[MsgType], 
        callback: Callable[[MsgType, str], None] | None = None
    ) -> Subscriber[MsgType]:
        return Subscriber(self.session, key_expr, msg_class, callback)
        
    def spin(self) -> None:
        """保持节点运行"""
        import time
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info(f"Node '{self.name}' 正在关闭...")
            self.session.close()