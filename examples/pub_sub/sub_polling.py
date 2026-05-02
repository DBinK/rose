from loguru import logger
from rich import print as rprint
from rose import Node

from msg import EnvSensorData

node = Node("data_logger")

sub = node.create_subscriber("room_a/sensor/env", EnvSensorData)

try:
    while True:
        msg, key = sub.recv()
        logger.success(f"收到 [{key}]:")
        rprint(msg)

except Exception as e:
    logger.error(e)

except KeyboardInterrupt:
    logger.info("用户中断，正在关闭节点...")
    
finally:
    node.close()
