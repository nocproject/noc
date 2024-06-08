# ----------------------------------------------------------------------
# Testing utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Dict, Any, List, Tuple
from contextlib import contextmanager
from dataclasses import dataclass

# Third-party modules
import orjson

# NOC modules
from noc.core.cdag.graph import CDAG
from noc.core.cdag.node.base import BaseCDAGNode
from noc.core.cdag.typing import ValueType
from noc.core.cdag.tx import Transaction
from noc.core.service.loader import get_service, set_service
from noc.core.service.stub import ServiceStub


class NodeCDAG(object):
    def __init__(self, node_type: str, config=None, state=None):
        self.cdag = CDAG("test", state or {})
        self.node = self.cdag.add_node("node", node_type, config=config)
        self.measure_node = self.cdag.add_node("measure", "none")
        self.node.subscribe(self.measure_node, "x")
        self.tx = self.cdag.begin()

    def get_node(self) -> BaseCDAGNode:
        return self.node

    def activate(self, name: str, value: ValueType):
        self.tx.activate("node", name, value)

    def get_value(self) -> Optional[ValueType]:
        """
        Get measured value, None if node is not activated
        :return:
        """
        i = self.tx.get_inputs(self.measure_node)
        return i.get("x")  # None node has `x` input

    def is_activated(self):
        return self.tx.get_inputs(self.measure_node).get("x") is not None

    def begin(self) -> Transaction:
        self.tx = self.cdag.begin()
        return self.tx

    def get_changed_state(self) -> Dict[Tuple[str, str], Any]:
        return self.tx.get_changed_state()


@contextmanager
def publish_service():
    """
    Publish-testing context

    Usage:

    with publish_service() as svc:
        ...
        msg = next(svc.iter_published())
    """
    prev_svc = get_service()
    svc = PublishStub()
    set_service(svc)
    yield svc
    set_service(prev_svc)


@dataclass
class PublishMsg(object):
    value: Any
    stream: str
    partition: Optional[int] = None
    key: Optional[bytes] = None
    headers: Optional[Dict[str, bytes]] = None


class PublishStub(ServiceStub):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages: List[PublishMsg] = []

    def publish(
        self,
        value: bytes,
        stream: str,
        partition: Optional[int] = None,
        key: Optional[bytes] = None,
        headers: Optional[Dict[str, bytes]] = None,
    ):
        self.messages.append(
            PublishMsg(
                value=orjson.loads(value),
                stream=stream,
                partition=partition,
                key=key,
                headers=headers,
            )
        )

    def iter_published(self):
        yield from self.messages
        self.messages = []
