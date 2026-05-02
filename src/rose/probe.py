import sys
import time
from collections import defaultdict

import zenoh
from loguru import logger
from rich import print as rprint


DISCOVERY_WAIT = 1.5  # 等待 peer 发现的时间 (秒)


def probe_network() -> None:
    session = zenoh.open(zenoh.Config())
    logger.info("获取系统全量拓扑...")

    # 给 Zenoh 一点时间通过多播发现网络中的其他 peer
    logger.debug(f"等待 {DISCOVERY_WAIT}s 完成 peer 发现...")
    time.sleep(DISCOVERY_WAIT)

    replies = session.liveliness().get("@rose/nodes/**")
    
    nodes_info: dict[str, dict[str, list[str]]] = defaultdict(
        lambda: {"pub": [], "sub": [], "server": [], "client": []}
    )
    
    key_expr_info: dict[str, dict[str, list[str]]] = defaultdict(
        lambda: {"pub_nodes": [], "sub_nodes": [], "server_nodes": [], "client_nodes": []}
    )

    found_any = False
    for reply in replies:
        if reply.ok:
            found_any = True
            token_key = str(reply.ok.key_expr)
            parts = token_key.split("/", 4)
            
            if len(parts) >= 5 and parts[0] == "@rose" and parts[1] == "nodes":
                node_name = parts[2]
                role = parts[3]       # "pub", "sub", "server", "client"
                actual_key_expr = parts[4]
                
                nodes_info[node_name][role].append(actual_key_expr)
                key_expr_info[actual_key_expr][f"{role}_nodes"].append(node_name)

    session.close()

    if found_any:
        logger.info("==== 节点 (Node) 视角 ====")
        rprint(dict(nodes_info))
        
        logger.info("==== Key Expression 视角 ====")
        clean_key_exprs = {
            expr: {k: v for k, v in roles.items() if v} 
            for expr, roles in key_expr_info.items()
        }
        rprint(clean_key_exprs)
    else:
        logger.warning("未发现活跃节点。请确认节点进程仍在运行，且未因执行完毕而退出。")


if __name__ == "__main__":
    # logger.remove()
    # logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")
    probe_network()