
import time
from collections import defaultdict
from typing import NamedTuple

import typer
import zenoh
from loguru import logger
from rich import print as rprint


class TopologyData(NamedTuple):
    nodes: dict[str, dict[str, list[str]]]
    topics: dict[str, dict[str, list[str]]]
    services: dict[str, dict[str, list[str]]]


def get_topology(session: zenoh.Session | None = None, discovery_wait: float = 0.3) -> TopologyData:
    """
    供 Python 代码或 CLI 调用的核心 API。
    如果未传入 session，内部会自动创建并在执行完毕后关闭。
    """
    owns_session = session is None
    if owns_session:
        session = zenoh.open(zenoh.Config())
        time.sleep(discovery_wait)

    replies = session.liveliness().get("@rose/nodes/**")
    
    nodes_raw: dict[str, dict[str, set[str]]] = defaultdict(
        lambda: {"pub": set(), "sub": set(), "server": set(), "client": set()}
    )
    topics_raw: dict[str, dict[str, set[str]]] = defaultdict(
        lambda: {"pub_nodes": set(), "sub_nodes": set()}
    )
    services_raw: dict[str, dict[str, set[str]]] = defaultdict(
        lambda: {"server_nodes": set(), "client_nodes": set()}
    )

    for reply in replies:
        if reply.ok:
            token_key = str(reply.ok.key_expr)
            parts = token_key.split("/", 4)
            
            if len(parts) >= 5 and parts[0] == "@rose" and parts[1] == "nodes":
                node_name = parts[2]
                role = parts[3]
                actual_key_expr = parts[4]
                
                nodes_raw[node_name][role].add(actual_key_expr)
                
                if role in ("pub", "sub"):
                    topics_raw[actual_key_expr][f"{role}_nodes"].add(node_name)
                elif role in ("server", "client"):
                    services_raw[actual_key_expr][f"{role}_nodes"].add(node_name)

    if owns_session:
        session.close()

    nodes_info = {n: {r: list(ks) for r, ks in data.items() if ks} for n, data in nodes_raw.items()}
    topics_info = {t: {r: list(ns) for r, ns in data.items() if ns} for t, data in topics_raw.items()}
    services_info = {s: {r: list(ns) for r, ns in data.items() if ns} for s, data in services_raw.items()}

    return TopologyData(nodes=nodes_info, topics=topics_info, services=services_info)


# ==========================================
# CLI 命令行应用部分
# ==========================================

ls_app = typer.Typer(help="快速查看全部信息")
app = typer.Typer(help="Rose 网络诊断命令行工具", no_args_is_help=True)
node_app = typer.Typer(help="节点相关操作", no_args_is_help=True)
topic_app = typer.Typer(help="发布/订阅相关操作", no_args_is_help=True)
service_app = typer.Typer(help="RPC 服务相关操作", no_args_is_help=True)


app.add_typer(ls_app, name="ls")
app.add_typer(node_app, name="node")
app.add_typer(topic_app, name="topic")
app.add_typer(service_app, name="service")


@app.callback()
def global_setup(ctx: typer.Context) -> None:
    # logger.remove()
    # logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")
    # CLI 调用 API 并挂载到上下文
    ctx.obj = get_topology()


@ls_app.callback(invoke_without_command=True)
def ls_default(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        rprint(ctx.obj)


@node_app.command("list")
def node_list(ctx: typer.Context) -> None:
    for node in ctx.obj.nodes.keys():
        print(node)


@node_app.command("info")
def node_info(ctx: typer.Context, target: str = typer.Argument(..., help="节点名称")) -> None:
    if target in ctx.obj.nodes:
        rprint(ctx.obj.nodes[target])
    else:
        logger.error(f"未找到节点: {target}")


@topic_app.command("list")
def topic_list(ctx: typer.Context) -> None:
    for topic in ctx.obj.topics.keys():
        print(topic)


@topic_app.command("info")
def topic_info(ctx: typer.Context, target: str = typer.Argument(..., help="Topic Key Expr")) -> None:
    if target in ctx.obj.topics:
        rprint(ctx.obj.topics[target])
    else:
        logger.error(f"未找到话题: {target}")


@service_app.command("list")
def service_list(ctx: typer.Context) -> None:
    for service in ctx.obj.services.keys():
        print(service)


@service_app.command("info")
def service_info(ctx: typer.Context, target: str = typer.Argument(..., help="Service Key Expr")) -> None:
    if target in ctx.obj.services:
        rprint(ctx.obj.services[target])
    else:
        logger.error(f"未找到服务: {target}")


if __name__ == "__main__":
    app()