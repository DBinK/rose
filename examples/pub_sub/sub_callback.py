from loguru import logger
from rich import print as rprint
from rose import Node

from msg import EnvSensorData

node = Node("data_logger")

# 定义回调函数 (享受 IDE 完美的参数补全)
def on_sensor_data(msg: EnvSensorData, source_key: str) -> None:
    logger.success(f"收到来自 [{source_key}] 的数据:")
    rprint(msg)  # 使用 rich 华丽地打印整个结构体和时间戳

# 声明订阅者 (甚至可以用通配符 room_a/sensor/*)
node.create_subscriber("room_a/sensor/env", EnvSensorData, on_sensor_data)

logger.success("日志节点已就绪，正在监听传感器网络...")
node.spin()
