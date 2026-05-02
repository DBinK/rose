"""测试共享 fixture"""

from collections.abc import Iterator

import pytest

from rose.node import Node


@pytest.fixture()
def node() -> Iterator[Node]:
    """创建一个 Node 实例并用完后自动关闭"""
    n = Node("test_node")
    yield n
    n.close()
