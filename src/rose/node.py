import queue
import time 
import msgspec
import zenoh
from loguru import logger
from typing import TypeVar, Callable, Generic

# 定义泛型，约束消息类型必须是 msgspec.Struct 的子类
MsgType = TypeVar("MsgType", bound=msgspec.Struct)

ReqType = TypeVar("ReqType", bound=msgspec.Struct)
ResType = TypeVar("ResType", bound=msgspec.Struct)

class Publisher(Generic[MsgType]):
    def __init__(self, session: zenoh.Session, key_expr: str):
        self._pub = session.declare_publisher(key_expr)
        self._encoder = msgspec.msgpack.Encoder()
    
    def publish(self, msg: MsgType) -> None:
        payload = self._encoder.encode(msg)  # 底层自动完成 msgpack 高速序列化
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
        self._decoder = msgspec.msgpack.Decoder(type=self._msg_class)
        
        if callback is not None:  # === 回调模式 ===
            def _zenoh_listener(sample: zenoh.Sample) -> None:
                try:
                    decoded_msg = self._decoder.decode(sample.payload.to_bytes())
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

        decoded = self._decoder.decode(sample.payload.to_bytes())
        return decoded, sample.key_expr


class Service(Generic[ReqType, ResType]):
    def __init__(
        self,
        session: zenoh.Session,
        key_expr: str,
        req_class: type[ReqType],
        res_class: type[ResType],
        callback: Callable[[ReqType], ResType]
    ):
        self._req_class = req_class
        self._res_class = res_class
        self._callback = callback
        
        self._decoder = msgspec.msgpack.Decoder(type=req_class)
        self._encoder = msgspec.msgpack.Encoder()

        def _query_handler(query: zenoh.Query) -> None:
            try:
                # 解析客户端发来的请求
                req_msg = self._decoder.decode(query.payload.to_bytes())
                
                # 执行用户的业务逻辑，获取响应对象
                res_msg = self._callback(req_msg)
                
                # 序列化响应对象并打回给客户端
                query.reply(query.key_expr, self._encoder.encode(res_msg))

            except msgspec.ValidationError as e:
                err_str = f"请求数据解析失败: {e}"
                logger.error(f"Service '{key_expr}' {err_str}")
                query.reply_err(err_str.encode('utf-8'))
                
            except Exception as e:
                err_str = f"业务逻辑执行异常: {e}"
                logger.error(f"Service '{key_expr}' {err_str}")
                query.reply_err(err_str.encode('utf-8'))

        # 声明一个 Queryable (即可查询的服务端点)
        self._queryable = session.declare_queryable(key_expr, _query_handler)
        self._liveliness_token = session.liveliness().declare_token(key_expr)


class Client(Generic[ReqType, ResType]):
    def __init__(
        self,
        session: zenoh.Session,
        key_expr: str,
        req_class: type[ReqType],
        res_class: type[ResType]
    ):
        self._key_expr = key_expr
        self.session = session
        self._encoder = msgspec.msgpack.Encoder()
        self._decoder = msgspec.msgpack.Decoder(type=res_class)

    def wait_for_service(self, timeout: float = 1.0) -> bool:
        """等待服务端就绪"""
        start_time = time.monotonic()
        while time.monotonic() - start_time < timeout:
            replies = self.session.liveliness().get(self._key_expr)
            for _ in replies:
                logger.success(f"服务 '{self._key_expr}' 已就绪！")
                return True
            time.sleep(0.1)
        return False

    def call(self, req: ReqType, timeout: float = 2.0) -> ResType:
        """同步阻塞调用服务"""
        payload = self._encoder.encode(req)
        
        # Zenoh 1.0 的优雅写法：直接拿回一个响应迭代器
        replies = self.session.get(
            self._key_expr, 
            payload=payload,
            target=zenoh.QueryTarget.BEST_MATCHING, 
            timeout=timeout  
        )
        
        # 遍历接收到的回复 (底层会自动处理阻塞等待)
        for reply in replies:
            if reply.ok:
                return self._decoder.decode(reply.ok.payload.to_bytes())
            else:  # 错误处理
                err_msg = reply.err.payload.to_string() if reply.err else "未知错误"
                raise RuntimeError(f"RPC 调用返回错误: {err_msg}")
                
        # 💡 如果能走到这里，说明 replies 是空的 (没找到服务端)
        raise TimeoutError(f"请求服务 '{self._key_expr}' 失败: 超时时间内无响应，可能原因：① Service 未启动 ② key_expr 不匹配 ③ 网络隔离/Discovery 延迟")


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
        
    def create_service(
        self,
        key_expr: str,
        req_class: type[ReqType],
        res_class: type[ResType],
        callback: Callable[[ReqType], ResType]
    ) -> Service[ReqType, ResType]:
        return Service(self.session, key_expr, req_class, res_class, callback)

    def create_client(
        self,
        key_expr: str,
        req_class: type[ReqType],
        res_class: type[ResType]
    ) -> Client[ReqType, ResType]:
        return Client(self.session, key_expr, req_class, res_class)

    def spin(self) -> None:
        """保持节点运行"""
        import time
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info(f"Node '{self.name}' 正在关闭...")
            self.session.close()