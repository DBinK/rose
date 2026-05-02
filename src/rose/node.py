# node.py

import queue
import time
from typing import Callable, Generic, TypeVar

import msgspec
import zenoh
from loguru import logger

from rose.message import Message

# 定义泛型，约束消息类型必须是 Message 的子类
MsgType = TypeVar("MsgType", bound=Message)   # 发布订阅消息类型
ReqType = TypeVar("ReqType", bound=Message)   # 服务请求消息类型
ResType = TypeVar("ResType", bound=Message)   # 服务响应消息类型


def _pin_token(session: zenoh.Session, token: object) -> None:
    """将活跃度 Token 锚定到 Session 上，防止 Python GC 误回收。

    Publisher / Client 等对象的回调不会持有 self 引用，
    当用户未保存返回值时对象会被 GC，导致 self._token 也被回收。
    将 token 锚定在模块级 dict 中，确保其生命周期与 session 一致。
    """
    sid = id(session)
    if sid not in _TOKEN_ANCHORS:
        _TOKEN_ANCHORS[sid] = []
    _TOKEN_ANCHORS[sid].append(token)


# 模块级 dict，锚定活跃度 Token 引用以防止 GC
_TOKEN_ANCHORS: dict[int, list[object]] = {}


class Publisher(Generic[MsgType]):
    def __init__(
        self,
        session: zenoh.Session,
        node_name: str,
        key_expr: str,
        msg_class: type[MsgType],
    ):
        self._pub = session.declare_publisher(key_expr)
        self._msg_class = msg_class
        self._encoder = msgspec.msgpack.Encoder()
        
        # 挂载活跃度 Token，格式定为：@rose/nodes/{节点名}/pub/{真实话题}
        clean_expr = key_expr.lstrip("/")
        self._token = session.liveliness().declare_token(f"@rose/nodes/{node_name}/pub/{clean_expr}")
        _pin_token(session, self._token)

    def publish(self, msg: MsgType) -> None:
        if not isinstance(msg, self._msg_class):
            raise TypeError(
                f"发布的消息类型必须是 {self._msg_class.__name__}，"
                f"实际传入的是 {type(msg).__name__}"
            )
        payload = self._encoder.encode(msg)
        self._pub.put(payload)


class Subscriber(Generic[MsgType]):
    def __init__(
        self, 
        session: zenoh.Session, 
        node_name: str,
        key_expr: str, 
        msg_class: type[MsgType], 
        callback: Callable[[MsgType, str], None] | None = None
    ):
        self._msg_class = msg_class
        self._callback = callback
        self._key_expr = key_expr
        self._decoder = msgspec.msgpack.Decoder(type=self._msg_class)

        clean_expr = key_expr.lstrip("/")  # 挂载活跃度 Token
        self._token = session.liveliness().declare_token(f"@rose/nodes/{node_name}/sub/{clean_expr}")
        _pin_token(session, self._token)

        if callback is not None:  # === 回调模式 ===
            def _zenoh_listener(sample: zenoh.Sample) -> None:
                try:
                    decoded_msg = self._decoder.decode(sample.payload.to_bytes())
                    self._callback(decoded_msg, sample.key_expr)
                except msgspec.ValidationError as e:
                    logger.error(f"key_expr '{key_expr}' 消息解析失败: {e}")
            self._sub = session.declare_subscriber(key_expr, _zenoh_listener)
        else:  # === 阻塞接收模式 ===
            self._queue: queue.Queue[zenoh.Sample] = queue.Queue()
            def _internal_listener(sample: zenoh.Sample) -> None:
                self._queue.put(sample)
            self._sub = session.declare_subscriber(key_expr, _internal_listener)


    def recv(self, timeout: float | None = None) -> tuple[MsgType, str] | None:
        """阻塞接收一条消息。"""
        if self._callback is not None:
            raise RuntimeError("该 Subscriber 使用回调模式，不支持 recv()")

        try:
            sample = self._queue.get(timeout=timeout)
        except queue.Empty:
            return None

        decoded = self._decoder.decode(sample.payload.to_bytes())
        return decoded, sample.key_expr


class Service(Generic[ReqType, ResType]):
    def __init__(
        self,
        session: zenoh.Session,
        node_name: str, 
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
                req_msg = self._decoder.decode(query.payload.to_bytes())
                res_msg = self._callback(req_msg)
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

        # 规范化路径结构
        clean_expr = key_expr.lstrip("/")
        self._token = session.liveliness().declare_token(f"@rose/nodes/{node_name}/server/{clean_expr}")
        _pin_token(session, self._token)


class Client(Generic[ReqType, ResType]):
    def __init__(
        self,
        session: zenoh.Session,
        node_name: str, 
        key_expr: str,
        req_class: type[ReqType],
        res_class: type[ResType]
    ):
        self._key_expr = key_expr
        self.session = session
        self._req_class = req_class
        self._res_class = res_class
        self._encoder = msgspec.msgpack.Encoder()
        self._decoder = msgspec.msgpack.Decoder(type=res_class)

        # 规范化路径结构
        clean_expr = key_expr.lstrip("/")
        self._token = session.liveliness().declare_token(f"@rose/nodes/{node_name}/client/{clean_expr}")
        _pin_token(session, self._token)

    def wait_for_service(self, timeout: float = 1.0) -> bool:
        """等待服务端就绪"""
        start_time = time.monotonic()
        clean_expr = self._key_expr.lstrip("/")
      
        query_expr = f"@rose/nodes/**/server/{clean_expr}"  # 使用通配符匹配任意提供该服务的 Node
        
        while time.monotonic() - start_time < timeout:
            replies = self.session.liveliness().get(query_expr)
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
        """创建一个 Node，作为 Zenoh 的会话容器，管理发布、订阅、服务和客户端"""
        self.name = name
        self.session = zenoh.open(zenoh.Config())  # 初始化通信引擎，默认自动多播发现
        self._closed = False
        logger.info(f"Node '{self.name}' 已启动")

    """使用 with 语句管理 Node 的生命周期"""
    def __enter__(self) -> "Node":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __del__(self) -> None:
        if not self._closed:
            self.close()

    def close(self) -> None:
        """优雅关闭节点：释放所有 Zenoh 资源"""
        if self._closed:
            return
        self._closed = True
        logger.info(f"Node '{self.name}' 正在关闭...")
        try:
            self.session.close()
        except Exception:
            pass

    # === 工厂方法，创建发布者、订阅者、服务和客户端 ===
    def create_publisher(self, key_expr: str, msg_class: type[MsgType]) -> Publisher[MsgType]:
        return Publisher(self.session, self.name, key_expr, msg_class)

    def create_subscriber(
        self, 
        key_expr: str, 
        msg_class: type[MsgType], 
        callback: Callable[[MsgType, str], None] | None = None
    ) -> Subscriber[MsgType]:
        return Subscriber(self.session, self.name, key_expr, msg_class, callback)
        
    def create_service(
        self,
        key_expr: str,
        req_class: type[ReqType],
        res_class: type[ResType],
        callback: Callable[[ReqType], ResType]
    ) -> Service[ReqType, ResType]:
        return Service(self.session, self.name, key_expr, req_class, res_class, callback)

    def create_client(
        self,
        key_expr: str,
        req_class: type[ReqType],
        res_class: type[ResType]
    ) -> Client[ReqType, ResType]:
        return Client(self.session, self.name, key_expr, req_class, res_class)

    # === 运行节点 ===
    def spin(self) -> None:
        """保持节点运行"""
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info(f"Node '{self.name}' 正在关闭...")
            self.session.close()