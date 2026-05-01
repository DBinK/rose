from loguru import logger
from rich import print as rprint
from rose import Node

from msg import EnvSensorData

node = Node("data_logger")

sub = node.create_subscriber("room_a/sensor/env", EnvSensorData)

while True:
    msg, key = sub.recv()
    logger.success(f"收到 [{key}]:")
    rprint(msg)
