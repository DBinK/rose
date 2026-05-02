from rose.probe import get_topology
from rich import print as rprint

# 获取当前运行状况数据
topology = get_topology()

rprint(topology)


"""

运行结果示例

> & c:/it/rose/.venv/Scripts/python.exe c:/it/rose/examples/debug/check_all_info.py

TopologyData(
    nodes={'math_server': {'server': ['math/add', 'math/div']}, 'data_logger': {'sub': ['room_a/sensor/env']}, 'sensor_hub_1': {'pub': ['room_a/sensor/env']}},
    topics={'room_a/sensor/env': {'pub_nodes': ['sensor_hub_1'], 'sub_nodes': ['data_logger']}},
    services={'math/add': {'server_nodes': ['math_server']}, 'math/div': {'server_nodes': ['math_server']}}
)

"""