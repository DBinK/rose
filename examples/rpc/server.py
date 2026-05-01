# --- examples/rpc/server.py ---
from loguru import logger
from rose import Node

from msg import AddIntsReq, AddIntsRes, DivFloatsReq, DivFloatsRes

def handle_add(req: AddIntsReq) -> AddIntsRes:
    logger.info(f"服务端收到计算请求: {req.a} + {req.b}")
    return AddIntsRes(sum=req.a + req.b)

def handle_div(req: DivFloatsReq) -> DivFloatsRes:
    logger.info(f"服务端收到计算请求: {req.a} / {req.b}")
    return DivFloatsRes(quotient=req.a / req.b)

node = Node("math_server")
node.create_service("math/add", AddIntsReq, AddIntsRes, handle_add)
node.create_service("math/div", DivFloatsReq, DivFloatsRes, handle_div)

logger.success("加法和除法服务已就绪，等待客户端调用...")
node.spin()