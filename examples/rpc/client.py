from rich import print as rprint
from rose import Node

from msg import AddIntsReq, AddIntsRes, DivFloatsReq, DivFloatsRes

# 创建节点
node = Node("math_client")

# ===== 加法测试 =====
add_client = node.create_client("math/add", AddIntsReq, AddIntsRes)
if not add_client.wait_for_service(timeout=3):
    print("服务端未就绪，请稍后再试")
    exit(1)

try:
    res = add_client.call(AddIntsReq(a=10, b=20))
    rprint(res)
except Exception as e:
    print(f"调用失败: {e}")

# ===== 除法测试 =====
div_client = node.create_client("math/div", DivFloatsReq, DivFloatsRes)
if not div_client.wait_for_service(timeout=3):
    print("服务端未就绪，请稍后再试")
    exit(1)

try:
    res = div_client.call(DivFloatsReq(a=10.0, b=2.0))  # 正常除法
    rprint(res)
except Exception as e:
    print(f"调用失败: {e}")

try:
    res = div_client.call(DivFloatsReq(a=10.0, b=0.0))  # 除数为0，应该会报错
    rprint(res)
except Exception as e:
    print(f"调用失败: {e}")

