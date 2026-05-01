import msgspec
import zenoh
from loguru import logger
from typing import TypeVar, Callable, Generic

# 定义泛型，约束消息类型必须是 msgspec.Struct 的子类
MsgType = TypeVar("MsgType", bound=msgspec.Struct)

class Publisher(Generic[MsgType]):
    def __init__(self, session: zenoh.Session, topic: str):
        self._pub = session.declare_publisher(topic)
        self.encoder = msgspec.msgpack.encode
    
    def publish(self, msg: MsgType) -> None:
        payload = self.encoder(msg)  # 底层自动完成 msgpack 高速序列化
        self._pub.put(payload)

class Subscriber(Generic[MsgType]):
    def __init__(
        self, 
        session: zenoh.Session, 
        topic: str, 
        msg_class: type[MsgType], 
        callback: Callable[[MsgType], None]
    ):
        self._msg_class = msg_class
        self._callback = callback
        self.decoder = msgspec.msgpack.decode
        
        # 内部闭包处理 zenoh 的原生回调
        def _zenoh_listener(sample: zenoh.Sample) -> None:
            try:  # ZBytes → bytes 转换后再反序列化 
                decoded_msg = self.decoder(sample.payload.to_bytes(), type=self._msg_class)
                self._callback(decoded_msg, sample.key_expr)
            except msgspec.ValidationError as e:
                logger.error(f"Topic '{topic}' 消息解析失败: {e}")

        self._sub = session.declare_subscriber(topic, _zenoh_listener)


class Node:
    def __init__(self, name: str):
        self.name = name
        # 初始化通信引擎，默认自动多播发现
        self.session = zenoh.open(zenoh.Config())
        logger.info(f"Node '{self.name}' 已启动")

    def create_publisher(self, topic: str, msg_class: type[MsgType]) -> Publisher[MsgType]:
        return Publisher(self.session, topic)

    def create_subscriber(
        self, 
        topic: str, 
        msg_class: type[MsgType], 
        callback: Callable[[MsgType], None]
    ) -> Subscriber[MsgType]:
        return Subscriber(self.session, topic, msg_class, callback)
        
    def spin(self) -> None:
        """保持节点运行"""
        import time
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info(f"Node '{self.name}' 正在关闭...")
            self.session.close()