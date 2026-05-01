from rose import Message

class EnvSensorData(Message):
    """环境传感器数据"""
    temperature: float
    humidity: float