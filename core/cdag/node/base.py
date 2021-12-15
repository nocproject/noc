# ----------------------------------------------------------------------
# BaseNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Optional, Type, Dict, List, Iterable, Tuple
from enum import Enum
import inspect
from dataclasses import dataclass
import sys

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


MASK_BOUND = 1 << 0
MASK_DYNAMIC = 1 << 1
MASK_KEY = 1 << 2


@dataclass
class Subscriber(object):
    __slots__ = ("node", "input", "next")
    node: "BaseCDAGNode"
    input: str
    next: Optional["Subscriber"]


class BaseCDAGNodeMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        n = type.__new__(mcs, name, bases, attrs)
        sig = inspect.signature(n.get_value)
        inputs = [sys.intern(x) for x in sig.parameters if x != "self"]
        if "kwargs" in inputs:
            n.allow_dynamic = True
            inputs.remove("kwargs")
        else:
            n.allow_dynamic = False
        n.static_inputs = inputs
        # Create slotted config class to optimize memory layout.
        # Slotted classes reduce memory usage by ~400 bytes, compared to Pydantic models
        if hasattr(n, "config_cls"):
            n.config_cls_slot = type(
                f"{n.config_cls.__name__}_Slot", (), {"__slots__": tuple(n.config_cls.__fields__)}
            )
        # Slotted state
        if hasattr(n, "state_cls"):
            n.state_cls_slot = type(
                f"{n.state_cls.__name__}_Slot", (), {"__slots__": tuple(n.state_cls.__fields__)}
            )
        #
        return n


class BaseCDAGNode(object, metaclass=BaseCDAGNodeMetaclass):
    name: str
    state_cls: Type[BaseModel]
    config_cls: Type[BaseModel]
    static_inputs: List[str]  # Filled by metaclass
    allow_dynamic: bool = False  # Filled by metaclass
    dot_shape: str = "box"
    categories: List[Category] = []
    config_cls_slot: Type  # Filled by metaclass
    state_cls_slot: Type  # Filled by metaclass

    __slots__ = (
        "node_id",
        "description",
        "state",
        "config",
        "_subscribers",
        "_inputs",
        "const_inputs",
        "_const_value",
        "sticky",
    )

    def __init__(
        self,
        node_id: str,
        state: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        sticky: bool = False,
    ):
        self.node_id = node_id
        self.description = description
        self.state = self.clean_state(state)
        self.config = self.clean_config(config)
        self._subscribers: Optional[Subscriber] = None
        self._inputs = {sys.intern(i): 0 for i in self.iter_inputs()}
        # # Pre-calculated inputs
        self.const_inputs: Optional[Dict[str, ValueType]] = None
        self._const_value: Optional[ValueType] = None
        self.sticky = sticky

    @classmethod
    def construct(
        cls,
        graph,
        node_id: str,
        description: Optional[str] = None,
        state: Optional[BaseModel] = None,
        config: Optional[BaseModel] = None,
        sticky: bool = False,
    ) -> Optional["BaseCDAGNode"]:
        """
        Construct node
        :return:
        """
        node = cls(node_id, description=description, state=state, config=config, sticky=sticky)
        graph.nodes[node_id] = node
        return node

    @staticmethod
    def slotify(slot_cls: Type, data: BaseModel) -> object:
        """
        Convert pydantic model to slotted class instance
        """
        o = slot_cls()
        for k in data.__fields__:
            setattr(o, k, getattr(data, k))
        return o

    def clone(self, graph, node_id: str) -> Optional["BaseCDAGNode"]:
        node = self.__class__(
            node_id,
            description=self.description,
            state={},
            config=self.config if hasattr(self, "config_cls") else None,
            sticky=self.sticky,
        )
        if self.allow_dynamic:
            for di in self.iter_mask_inputs(MASK_DYNAMIC):
                node.add_input(di)
        graph.nodes[node_id] = node
        return node

    def clean_state(self, state: Optional[Dict[str, Any]]) -> Optional[BaseModel]:
        if not hasattr(self, "state_cls"):
            return None
        state = state or {}
        c_state = self.state_cls(**state)
        return self.slotify(self.state_cls_slot, c_state)

    def clean_config(self, config: Optional[Dict[str, Any]]) -> Optional[BaseModel]:
        if not hasattr(self, "config_cls") or config is None:
            return None
        # Shortcut, if config is already cleaned (cloned copies)
        if isinstance(config, BaseModel) or hasattr(config, "__slots__"):
            return config
        # Slotify to reduce memory usage
        cfg = self.config_cls(**config)
        return self.slotify(self.config_cls_slot, cfg)

    def iter_inputs(self) -> Iterable[str]:
        """
        Enumerate all configured inputs
        :return:
        """
        inputs = getattr(self, "_inputs", self.static_inputs)
        yield from inputs

    def iter_unbound_inputs(self) -> Iterable[str]:
        """
        Iterate all unbound inputs
        :return:
        """
        for i in self.iter_inputs():
            if not self._inputs[i] & MASK_BOUND:
                yield i

    def iter_mask_inputs(self, mask: int) -> Iterable[str]:
        """
        Iterate all inputs matching mask
        """
        for i, flag in self._inputs.items():
            if flag & mask:
                yield i

    def iter_key_inputs(self) -> Iterable[str]:
        """
        Iterate all key inputs
        """
        yield from self.iter_mask_inputs(MASK_KEY)

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
        if inputs[name] is not None:
            return  # Already activated
        inputs[name] = value  # Activate input
        if any(True for n, v in inputs.items() if v is None and self.is_required_input(n)):
            return  # Non-activated inputs
        # Activate node, calculate value
        value = self.get_value(**inputs)
        if hasattr(self, "state_cls"):
            tx.update_state(self)
        # Notify all subscribers
        if value is not None:
            for s in self.iter_subscribers():
                s.node.activate(tx, s.input, value)

    def is_required_input(self, name: str) -> bool:
        """
        Check if input is required
        """
        return not self.is_dynamic_input(name)

    def is_dynamic_input(self, name: str) -> bool:
        """
        Check if input is dynamic
        :param name:
        :return:
        """
        return bool(self._inputs.get(name, 0) & MASK_DYNAMIC)

    def is_const_input(self, name: str) -> bool:
        """
        Check if input is const
        """
        return self.const_inputs is not None and name in self.const_inputs

    def is_key_input(self, name: str) -> bool:
        """
        Check if input is key
        :param name:
        :return:
        """
        return bool(self._inputs.get(name, 0) & MASK_KEY)

    def activate_const(self, name: str, value: ValueType) -> None:
        """
        Activate const input. Called during construction time.

        :param name:
        :param value:
        :return:
        """
        name = sys.intern(name)
        if name not in self._inputs:
            raise KeyError(f"Invalid const input: {name}")
        if self.const_inputs is None:
            self.const_inputs = {}
        self.const_inputs[name] = value
        if self.is_const:
            for s in self.iter_subscribers():
                s.node.activate_const(s.input, self._const_value)

    def subscribe(self, node: "BaseCDAGNode", name: str, dynamic: bool = False) -> None:
        """
        Subscribe to node activation
        :param node: Connected node
        :param name: Connected input name
        :param dynamic: Create input when necessary
        :return:
        """
        if node == self:
            raise ValueError("Cannot subscribe to self")
        name = sys.intern(name)
        if self.has_subscriber(node, name):
            return
        if dynamic:
            node.add_input(name)
        self._subscribers = Subscriber(node=node, input=name, next=self._subscribers)
        node.mark_as_bound(name)
        if self.is_const:
            node.activate_const(name, self._const_value)

    def mark_as_bound(self, name: str) -> None:
        """
        Mark input as bound
        """
        if name in self._inputs:
            self._inputs[name] |= MASK_BOUND

    def mark_as_key(self, name: str) -> None:
        """
        Mark input as key
        """
        if name in self._inputs:
            self._inputs[name] |= MASK_KEY

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
        if self.state:
            return self.state_cls(
                **{s: getattr(self.state, s) for s in self.state_cls_slot.__slots__}
            )
        return None

    def iter_subscribers(self) -> Iterable[Subscriber]:
        """
        Iterate all subscribers for node
        """
        s = self._subscribers
        while s:
            yield s
            s = s.next

    def has_subscriber(self, node: "BaseCDAGNode", input: str) -> bool:
        return any(True for s in self.iter_subscribers() if s.node == node and s.input == input)

    @property
    def is_const(self) -> bool:
        """
        Check if the node is constant value
        :return:
        """
        if self._const_value is not None:
            return True
        const_inputs = self.const_inputs if self.const_inputs is not None else {}
        if len(const_inputs) != len(self._inputs):
            return False
        self._const_value = self.get_value(**const_inputs)
        return True

    def add_input(self, name: str, is_key: bool = False) -> None:
        """
        Add new dynamic input
        :param name: Input name
        :return:
        """
        name = sys.intern(name)
        if name in self._inputs:
            return
        if not self.allow_dynamic:
            raise TypeError("Dynamic inputs are not allowed")
        flag = MASK_DYNAMIC
        if is_key:
            flag |= MASK_KEY
        self._inputs[name] = flag

    def iter_config_fields(self) -> Iterable[str]:
        """
        Iterate config field names
        """
        if hasattr(self, "config_cls"):
            yield from self.config_cls_slot.__slots__

    def iter_initial_inputs(self) -> Iterable[Tuple[str, Optional[ValueType]]]:
        """
        Iterate transaction initial inputs
        """
        if self.const_inputs:
            for i in self._inputs:
                yield i, self.const_inputs.get(i)
        else:
            for i in self._inputs:
                yield i, None
