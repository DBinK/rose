from rich import print as rprint
from rose import Node

from msg import AddIntsReq, AddIntsRes, DivFloatsReq, DivFloatsRes

node = Node("math_client")
client = node.create_client("math/add", AddIntsReq, AddIntsRes)

res = client.wait_for_service(timeout=1.0)
if not res:
    print("服务端未就绪，请稍后再试")
    exit(1)

res = client.call(AddIntsReq(a=10, b=20))

print(f"结果是:") 
rprint(res)

client = node.create_client("math/div", DivFloatsReq, DivFloatsRes)
res = client.wait_for_service(timeout=1.0)
if not res:
    print("服务端未就绪，请稍后再试")
    exit(1)

# res = client.call(DivFloatsReq(a=10.0, b=2.0))
res = client.call(DivFloatsReq(a=10.0, b=0.0))  # 除数为0，应该会报错

print(f"结果是:") 
rprint(res)
