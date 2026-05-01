import time
from loguru import logger
from rose import Node

from msg import EnvSensorData

# 1. 初始化节点
node = Node("sensor_hub_1")

# 2. 声明发布者，绑定 Key Expression 和消息类型
pub = node.create_publisher("room_a/sensor/env", EnvSensorData)

logger.success("传感器节点启动，开始广播数据...")

try:
    temp = 25.0
    while True:
        # 3. 实例化消息 (Header 的时间戳会自动生成)
        msg = EnvSensorData(
            header={"frame_id": "sensor_link_1"}, # 可选覆盖，不写则为空
            temperature=temp,
            humidity=60.5
        )
        
        # 发布数据！
        pub.publish(msg)
        logger.info(f"已发送 -> 温度: {msg.temperature}°C")
        
        temp += 0.1 # 模拟温度变化
        time.sleep(1)
        
except KeyboardInterrupt:
    logger.info("节点关闭")
