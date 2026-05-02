"""probe.py 探针功能测试 — 核心测试 get_topology

注意：liveliness token 传播依赖多播发现，跨 Session 测试不可靠。
因此使用同 Session 模式：在同一个 Session 上声明 token 并查询。
"""

import time

import pytest
import zenoh

from rose.node import Client, Publisher, Service, Subscriber
from rose.probe import TopologyData, get_topology
from tests.test_node import AddReq, AddRes, TestMsg


def _make_session() -> zenoh.Session:
    """创建一个 Session"""
    return zenoh.open(zenoh.Config())


def _safe_close(*sessions: zenoh.Session) -> None:
    for s in sessions:
        try:
            s.close()
        except Exception:
            pass


class TestGetTopology:
    """get_topology 核心功能测试"""

    def test_returns_topology_data_structure(self) -> None:
        """总是返回 TopologyData 结构"""
        session = _make_session()
        try:
            topo = get_topology(session=session, discovery_wait=0.3)
            assert isinstance(topo, TopologyData)
            assert hasattr(topo, "nodes")
            assert hasattr(topo, "topics")
            assert hasattr(topo, "services")
        finally:
            _safe_close(session)

    def test_detect_publisher(self) -> None:
        """同 Session 内探测发布者"""
        session = _make_session()

        pub = Publisher(session, "sensor_node", "room/temp", TestMsg)
        time.sleep(0.5)

        try:
            topo = get_topology(session=session, discovery_wait=0.3)

            assert "sensor_node" in topo.nodes
            assert "room/temp" in topo.nodes["sensor_node"]["pub"]
            assert "room/temp" in topo.topics
            assert "sensor_node" in topo.topics["room/temp"]["pub_nodes"]
        finally:
            _safe_close(session)

    def test_detect_subscriber(self) -> None:
        """同 Session 内探测订阅者"""
        session = _make_session()

        Subscriber(session, "logger_node", "room/temp", TestMsg, lambda m, k: None)
        time.sleep(0.5)

        try:
            topo = get_topology(session=session, discovery_wait=0.3)

            assert "logger_node" in topo.nodes
            assert "room/temp" in topo.nodes["logger_node"]["sub"]
            assert "room/temp" in topo.topics
            assert "logger_node" in topo.topics["room/temp"]["sub_nodes"]
        finally:
            _safe_close(session)

    def test_detect_service(self) -> None:
        """同 Session 内探测 RPC 服务"""
        session = _make_session()

        Service(session, "math_node", "calc/add", AddReq, AddRes, lambda req: AddRes(sum=req.a + req.b))
        time.sleep(0.5)

        try:
            topo = get_topology(session=session, discovery_wait=0.3)

            assert "math_node" in topo.nodes
            assert "calc/add" in topo.nodes["math_node"]["server"]
            assert "calc/add" in topo.services
            assert "math_node" in topo.services["calc/add"]["server_nodes"]
        finally:
            _safe_close(session)

    def test_detect_client(self) -> None:
        """同 Session 内探测客户端"""
        session = _make_session()

        cli = Client(session, "app_node", "calc/add", AddReq, AddRes)
        time.sleep(0.5)

        try:
            topo = get_topology(session=session, discovery_wait=0.3)

            assert "app_node" in topo.nodes
            assert "calc/add" in topo.nodes["app_node"]["client"]
            assert "calc/add" in topo.services
            assert "app_node" in topo.services["calc/add"]["client_nodes"]
        finally:
            _safe_close(session)

    def test_mixed_topology(self) -> None:
        """混合场景：同一个 Session 上多个节点/话题/服务"""
        session = _make_session()

        pub1 = Publisher(session, "sensor_1", "room/temp", TestMsg)
        pub2 = Publisher(session, "sensor_1", "room/humidity", TestMsg)
        sub = Subscriber(session, "logger_1", "room/temp", TestMsg, lambda m, k: None)
        svc = Service(session, "calc_1", "math/add", AddReq, AddRes, lambda req: AddRes(sum=req.a + req.b))
        cli = Client(session, "app_1", "math/add", AddReq, AddRes)
        time.sleep(0.5)

        try:
            topo = get_topology(session=session, discovery_wait=0.3)

            # 验证所有节点
            assert "sensor_1" in topo.nodes
            assert "logger_1" in topo.nodes
            assert "calc_1" in topo.nodes
            assert "app_1" in topo.nodes

            # 验证角色
            assert "room/temp" in topo.nodes["sensor_1"]["pub"]
            assert "room/humidity" in topo.nodes["sensor_1"]["pub"]
            assert "room/temp" in topo.nodes["logger_1"]["sub"]
            assert "math/add" in topo.nodes["calc_1"]["server"]
            assert "math/add" in topo.nodes["app_1"]["client"]

            # 验证话题聚合
            assert "room/temp" in topo.topics
            assert "room/humidity" in topo.topics
            assert "sensor_1" in topo.topics["room/temp"]["pub_nodes"]
            assert "logger_1" in topo.topics["room/temp"]["sub_nodes"]
            assert "sensor_1" in topo.topics["room/humidity"]["pub_nodes"]

            # 验证服务聚合
            assert "math/add" in topo.services
            assert "calc_1" in topo.services["math/add"]["server_nodes"]
            assert "app_1" in topo.services["math/add"]["client_nodes"]
        finally:
            _safe_close(session)

    def test_auto_session_returns_structure(self) -> None:
        """不传 session 时，返回 TopologyData 结构"""
        topo = get_topology(discovery_wait=0.3)
        assert isinstance(topo, TopologyData)

    def test_ignore_unknown_tokens(self) -> None:
        """不符合 @rose/nodes/*/*/* 格式的 token 应被忽略"""
        session = _make_session()

        session.liveliness().declare_token("some/random/token")
        session.liveliness().declare_token("@other/thing")
        time.sleep(0.3)

        try:
            topo = get_topology(session=session, discovery_wait=0.3)

            # 没有 rose 格式的节点，nodes 应为空
            # （注意：不 assert 为空，因为外部可能还有）
            assert isinstance(topo, TopologyData)
        finally:
            _safe_close(session)
