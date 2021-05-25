# ----------------------------------------------------------------------
# BaseNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Set, Optional, Type, Dict, List, Iterable, Tuple
from enum import Enum
import inspect

# Third-party modules
from pydantic import BaseModel

# NOC modules
from ..typing import ValueType
from ..tx import Transaction


class Category(str, Enum):
    MATH = "math"
    OPERATION = "operation"
    LOGICAL = "logical"
    ACTIVATION = "activation"
    COMPARE = "compare"
    DEBUG = "debug"
    UTIL = "util"
    STATISTICS = "statistics"
    ML = "ml"
    WINDOW = "window"


class BaseCDAGNodeMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        n = type.__new__(mcs, name, bases, attrs)
        sig = inspect.signature(n.get_value)
        inputs = [x for x in sig.parameters if x != "self"]
        if "kwargs" in inputs:
            n.allow_dynamic = True
            inputs.remove("kwargs")
        else:
            n.allow_dynamic = False
        n.static_inputs = inputs
        return n


class BaseCDAGNode(object, metaclass=BaseCDAGNodeMetaclass):
    name: str
    state_cls: Type[BaseModel]
    config_cls: Type[BaseModel]
    static_inputs: List[str]  # Filled by metaclass
    allow_dynamic: bool = False  # Filled by metaclass
    dot_shape: str = "box"
    categories: List[Category] = []

    def __init__(
        self,
        node_id: str,
        state: Optional[Dict[str, Any]] = None,
        description: str = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.node_id = node_id
        self.description = description
        self.state = self.clean_state(state)
        self.config = self.clean_config(config)
        self._subscribers: List[Tuple[BaseCDAGNode, str]] = []
        # Pre-calculated inputs
        self.const_inputs: Dict[str, ValueType] = {}
        self._const_value: Optional[ValueType] = None
        # Manually-configured dynamic inputs
        self._dynamic_inputs: Set[str] = set()
        # All inputs
        self._inputs = {i for i in self.iter_inputs()}
        self._bound_inputs: Set[str] = set()

    @classmethod
    def construct(
        cls,
        graph,
        node_id: str,
        description: Optional[str],
        state: Optional[BaseModel],
        config: Optional[BaseModel],
        ctx: Optional[Dict[str, Any]],
    ) -> Optional["BaseCDAGNode"]:
        """
        Construct node
        :return:
        """
        node = cls(node_id, description=description, state=state, config=config)
        graph.nodes[node_id] = node
        return node

    def clean_state(self, state: Optional[Dict[str, Any]]) -> Optional[BaseModel]:
        if not hasattr(self, "state_cls"):
            return None
        state = state or {}
        return self.state_cls(**state)

    def clean_config(self, config: Optional[Dict[str, Any]]) -> Optional[BaseModel]:
        if not hasattr(self, "config_cls"):
            return None
        return self.config_cls(**config)

    def iter_inputs(self) -> Iterable[str]:
        """
        Enumerate all configured inputs
        :return:
        """
        yield from self.static_inputs
        yield from self._dynamic_inputs

    def iter_unbound_inputs(self) -> Iterable[str]:
        """
        Iterate all unbound inputs
        :return:
        """
        for i in self.iter_inputs():
            if i not in self._bound_inputs:
                yield i

    def activate(self, tx: Transaction, name: str, value: ValueType) -> None:
        """
        Activate named input with
        :param tx: Transaction instance
        :param name: Input name
        :param value: Input value
        :return:
        """
        if name not in self._inputs:
            raise KeyError(f"Invalid input: {name}")
        inputs = tx.get_inputs(self)
        is_active = inputs[name] is not None
        inputs[name] = value
        if is_active or any(
            True for n, v in inputs.items() if v is None and self.is_required_input(n)
        ):
            return  # Already activated or non-activated inputs
        # Activate node, calculate value
        value = self.get_value(**inputs)
        if hasattr(self, "state_cls"):
            tx.update_state(self)
        # Notify all subscribers
        if value is not None:
            for s_node, s_name in self._subscribers:
                s_node.activate(tx, s_name, value)

    def is_required_input(self, name: str) -> bool:
        return name not in self._dynamic_inputs

    def activate_const(self, name: str, value: ValueType) -> None:
        """
        Activate const input. Called during construction time.

        :param name:
        :param value:
        :return:
        """
        if name not in self._inputs:
            raise KeyError(f"Invalid const input: {name}")
        self.const_inputs[name] = value
        if self.is_const:
            for node, name in self._subscribers:
                node.activate_const(name, self._const_value)

    def subscribe(self, node: "BaseCDAGNode", name: str, dynamic: bool = False) -> None:
        """
        Subscribe to node activation
        :param node: Connected node
        :param name: Connected input name
        :param dynamic: Create input when necessary
        :return:
        """
        if dynamic:
            node.add_input(name)
        self._subscribers += [(node, name)]
        node.mark_as_bound(name)
        if self.is_const:
            node.activate_const(name, self._const_value)

    def mark_as_bound(self, name: str) -> None:
        if name in self._inputs:
            self._bound_inputs.add(name)

    def get_value(self, *args, **kwargs) -> Optional[ValueType]:  # pragma: no cover
        """
        Calculate node value. Returns None when input is malformed and should not be propagated
        :return:
        """
        raise NotImplementedError

    def get_state(self) -> Optional[BaseModel]:
        """
        Get current node state
        :return:
        """
        return self.state

    def iter_subscribers(self) -> Iterable[Tuple["BaseCDAGNode", str]]:
        for node, name in self._subscribers:
            yield node, name

    @property
    def is_const(self) -> bool:
        """
        Check if the node is constant value
        :return:
        """
        if self._const_value is not None:
            return True
        if len(self.const_inputs) != len(self._inputs):
            return False
        self._const_value = self.get_value(**self.const_inputs)
        return True

    def add_input(self, name: str) -> None:
        """
        Add new dynamic input
        :param name: Input name
        :return:
        """
        if name in self._inputs:
            return
        if not self.allow_dynamic:
            raise TypeError("Dynamic inputs are not allowed")
        self._inputs.add(name)
        self._dynamic_inputs.add(name)
