# ----------------------------------------------------------------------
# BaseNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Optional, Type, Dict, List, Iterable, Set, Union
from enum import Enum
import inspect
from dataclasses import dataclass
import sys

# Third-party modules
from pydantic import BaseModel

# NOC modules
from ..typing import ValueType
from ..tx import Transaction

# Input types
IN_INVALID = 0
IN_REQUIRED = 1
IN_OPTIONAL = 2


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


@dataclass
class Subscriber(object):
    __slots__ = ("node", "input", "next")
    node: "BaseCDAGNode"
    input: str
    next: Optional["Subscriber"]


config_proxy_sentinel = object()


class ConfigProxy(object):
    """
    Wrap BaseModel and override particular attributes
    """

    __slots__ = ("__base", "__override", "__static")

    def __init__(
        self, base: BaseModel, override: Dict[str, Any], static: Optional[Dict[str, Any]] = None
    ):
        """
        Base Configuration (on BaseModel)
        :param base:
        :param override: Override part of config, used for override config param
        :param static: Static part of config, used for store values on ConfigStore
        """
        self.__base = base
        self.__override = override
        self.__static = static

    def __getattribute__(self, __name: str) -> Any:
        if __name.startswith("_"):
            return super().__getattribute__(__name)
        if self.__static and __name in self.__static:
            return self.__static[__name]
        v = self.__override.get(__name, config_proxy_sentinel)
        if v is config_proxy_sentinel:
            return getattr(self.__base, __name)
        return v


class BaseCDAGNodeMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        n = type.__new__(mcs, name, bases, attrs)
        sig = inspect.signature(n.get_value)
        n.allow_dynamic = "kwargs" in sig.parameters
        n.static_inputs = {sys.intern(x) for x in sig.parameters if x not in ("self", "kwargs")}
        n.req_inputs_count = len(n.static_inputs)
        # Create slotted config class to optimize memory layout.
        # Slotted classes reduce memory usage by ~400 bytes, compared to Pydantic models
        if hasattr(n, "config_cls"):
            n.config_cls_slot = type(
                f"{n.config_cls.__name__}_Slot",
                (),
                {"__slots__": tuple(sys.intern(x) for x in n.config_cls.model_fields)},
            )
        # Slotted state
        if hasattr(n, "state_cls"):
            state_slots = tuple(sys.intern(x) for x in n.state_cls.model_fields)
            req_state_fields = [k for k, v in n.state_cls.model_fields.items() if v.is_required()]
            opt_state_fields = [
                k for k, v in n.state_cls.model_fields.items() if not v.is_required()
            ]
            # Generate dict-getter code
            dict_fn = ["def dict(self):"]
            if opt_state_fields:
                dict_fn += ["    x = {"]
                dict_fn += [f"        '{s}': self.{s}," for s in req_state_fields]
                dict_fn += ["    }"]
                for opt in opt_state_fields:
                    dict_fn += [
                        f"    if self.{opt} is not None:",
                        f"        x['{opt}'] = self.{opt}",
                    ]
                dict_fn += ["    return x"]
            else:
                # No optional fields, streamlined implementation
                dict_fn += ["    return {"]
                dict_fn += [f"        '{s}': self.{s}," for s in state_slots]
                dict_fn += ["    }"]
            # Compile and execute dict-getter to get function
            co = compile("\n".join(dict_fn), "<string>", "exec")
            l_vars = {}
            exec(co, {}, l_vars)  # l_vars will contain 'dict'
            n.state_cls_slot = type(
                f"{n.state_cls.__name__}_Slot",
                (),
                {"__slots__": state_slots, "dict": l_vars["dict"]},
            )
        #
        return n


class BaseCDAGNode(object, metaclass=BaseCDAGNodeMetaclass):
    name: str
    state_cls: Type[BaseModel]
    config_cls: Type[BaseModel]
    static_inputs: Set[str]  # Filled by metaclass
    # Required inputs count, filled by metaclass
    req_inputs_count: int = 0
    allow_dynamic: bool = False  # Filled by metaclass
    dot_shape: str = "box"
    categories: List[Category] = []
    config_cls_slot: Type  # Filled by metaclass
    state_cls_slot: Type  # Filled by metaclass

    __slots__ = (
        "_node_id",
        "_prefix",
        "description",
        "state",
        "config",
        "_subscribers",
        "bound_inputs",
        "dynamic_inputs",
        "const_inputs",
        "_const_value",
        "sticky",
    )

    def __init__(
        self,
        node_id: str,
        prefix: Optional[str] = None,
        state: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        sticky: bool = False,
    ):
        self._node_id = sys.intern(node_id)
        self._prefix = sys.intern(prefix) if prefix else None
        self.description = description
        self.state = self.clean_state(state)
        self.config = self.clean_config(config)
        self._subscribers: Optional[Subscriber] = None
        self.bound_inputs: Optional[Set[str]] = None  # Lives until .freeze()
        self.dynamic_inputs: Optional[Dict[str, bool]] = None
        # # Pre-calculated inputs
        self.const_inputs: Optional[Dict[str, ValueType]] = None
        self._const_value: Optional[ValueType] = None
        self.sticky = sticky

    @property
    def node_id(self):
        if self._prefix:
            return f"{self._prefix}::{self._node_id}"
        return self._node_id

    @classmethod
    def construct(
        cls,
        node_id: str,
        prefix: Optional[str] = None,
        description: Optional[str] = None,
        state: Optional[BaseModel] = None,
        config: Optional[BaseModel] = None,
        sticky: bool = False,
    ) -> Optional["BaseCDAGNode"]:
        """
        Construct node
        :return:
        """
        return cls(
            node_id,
            prefix=prefix,
            description=description,
            state=state,
            config=config,
            sticky=sticky,
        )

    @staticmethod
    def slotify(slot_cls: Type, data: BaseModel) -> object:
        """
        Convert pydantic model to slotted class instance
        """
        o = slot_cls()
        for k in data.model_fields:
            setattr(o, k, getattr(data, k))
        return o

    def clone(
        self,
        node_id: str,
        prefix: Optional[str] = None,
        state: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        static_config: Optional[Dict[str, Any]] = None,
    ) -> Optional["BaseCDAGNode"]:
        """
        Clone node
        :param node_id: Node Identifier
        :param prefix: Node Identifier prefix for create unique identifier
        :param state: Node state
        :param config: Config params for node
        :param static_config: May be split config to two parts
        :return:
        """
        if not hasattr(self, "config_cls"):
            cfg = None
        elif config:
            cfg = ConfigProxy(self.config, config, static_config)
        else:
            cfg = self.config

        node = self.__class__(
            node_id,
            prefix=prefix,
            description=self.description,
            state=state,
            config=cfg,
            sticky=self.sticky,
        )
        if self.allow_dynamic and self.dynamic_inputs:
            for di, is_key in self.dynamic_inputs.items():
                node.add_input(di, is_key=is_key)
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
        if isinstance(config, (BaseModel, ConfigProxy)) or hasattr(config, "__slots__"):
            return config
        # Slotify to reduce memory usage
        cfg = self.config_cls(**config)
        return self.slotify(self.config_cls_slot, cfg)

    def iter_inputs(self) -> Iterable[str]:
        """
        Enumerate all configured inputs
        :return:
        """
        yield from self.static_inputs
        if self.allow_dynamic and self.dynamic_inputs:
            yield from self.dynamic_inputs

    def first_input(self) -> Optional[str]:
        """
        Get first input name
        """
        try:
            return next(self.iter_inputs())
        except StopIteration:
            return None

    def iter_unbound_inputs(self) -> Iterable[str]:
        """
        Iterate all unbound inputs
        :return:
        """
        if not self.bound_inputs:
            yield from self.iter_inputs()
            return
        for i in self.iter_inputs():
            if i not in self.bound_inputs:
                yield i

    def get_input_type(self, name: str) -> int:
        """
        Returns input type:
        * IN_INVALID - for non-existing input
        * IN_REQUIRED - for required input
        * IN_OPTIONAL - for dynamic input

        :param name: Input name
        :returns: input type as IN_*
        """
        if name in self.static_inputs:
            return IN_REQUIRED
        if self.allow_dynamic and self.dynamic_inputs and name in self.dynamic_inputs:
            return IN_OPTIONAL
        return IN_INVALID

    def has_input(self, name: str) -> bool:
        """
        Check if the node has input with given name
        :param name: name of input
        :returns: True, if input exists
        """
        return self.get_input_type(name) != IN_INVALID

    def activate(self, tx: Transaction, name: str, value: Union[ValueType, str]) -> None:
        """
        Activate named input with
        :param tx: Transaction instance
        :param name: Input name
        :param value: Input value
        :return:
        """
        # Check for valid input name
        in_type = self.get_input_type(name)
        if in_type == IN_INVALID:
            raise KeyError(f"Invalid input {name}")
        # Get collected inputs
        inputs = tx.get_inputs(self)
        if inputs.get(name) is not None:
            return  # Already activated
        # Activate input
        inputs[name] = value
        # Optional inputs cannon trigger the activation
        if in_type == IN_OPTIONAL:
            return
        # Check if all required inputs are activated
        if not tx.is_ready(self):
            return  # Not all required inputs are activated
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
        return self.get_input_type(name) == IN_REQUIRED

    def is_dynamic_input(self, name: str) -> bool:
        """
        Check if input is dynamic
        :param name:
        :return:
        """
        return self.get_input_type(name) == IN_OPTIONAL

    def is_key_input(self, name: str) -> bool:
        """
        Check if input is key one
        """
        return (
            self.allow_dynamic
            and self.dynamic_inputs
            and bool(self.dynamic_inputs.get(name, False))
        )

    def is_const_input(self, name: str) -> bool:
        """
        Check if input is const
        """
        return self.const_inputs is not None and name in self.const_inputs

    def activate_const(self, name: str, value: ValueType) -> None:
        """
        Activate const input. Called during construction time.

        :param name:
        :param value:
        :return:
        """
        name = sys.intern(name)
        if self.get_input_type(name) == IN_INVALID:
            raise KeyError(f"Invalid input {name}")
        if self.const_inputs is None:
            self.const_inputs = {}
        self.const_inputs[name] = value
        if self.is_const:
            for s in self.iter_subscribers():
                s.node.activate_const(s.input, self._const_value)

    def subscribe(
        self, node: "BaseCDAGNode", name: str, dynamic: bool = False, mark_bound: bool = True
    ) -> None:
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
        if mark_bound:
            node.mark_as_bound(name)
        if self.is_const:
            node.activate_const(name, self._const_value)

    def mark_as_bound(self, name: str) -> None:
        """
        Mark input as bound
        """
        name = sys.intern(name)
        if not self.has_input(name):
            return
        if self.bound_inputs is None:
            self.bound_inputs = {name}
        else:
            self.bound_inputs.add(name)

    def unsubscribe(self, node: "BaseCDAGNode", name: Optional[str] = None) -> None:
        """
        Unsubscribe node
        :param node: Connected node
        :param name: Connected input name
        :return:
        """
        if node == self:
            raise ValueError("Cannot subscribe to self")
        name = sys.intern(name)
        if not self.has_subscriber(node, name):
            return
        # Cleanup const
        if self.is_const_input(name):
            del self.const_inputs[name]
        # Cleanup input
        if self.is_dynamic_input(name):
            del self.dynamic_inputs[name]
        # Remove Subscriber
        prev = None
        for s in self.iter_subscribers():
            if s.node != node and s.input != name:
                prev = s
                continue
            if not prev:
                self._subscribers = None
            elif s.next:
                prev.next = s.next
            else:
                prev.next = None
            break

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
        n_inputs = len(self.static_inputs)
        if self.allow_dynamic and self.dynamic_inputs:
            n_inputs += len(self.dynamic_inputs)
        const_inputs = self.const_inputs if self.const_inputs is not None else {}
        if len(const_inputs) != n_inputs:
            return False
        # Activate const
        self._const_value = self.get_value(**const_inputs)
        return True

    def add_input(self, name: str, is_key: bool = False) -> None:
        """
        Add new dynamic input
        :param name: Input name
        :param is_key:
        :return:
        """
        if not self.allow_dynamic:
            raise TypeError("Dynamic inputs are not allowed")
        name = sys.intern(name)
        if self.has_input(name):
            return
        if self.dynamic_inputs is None:
            self.dynamic_inputs = {name: is_key}
        else:
            self.dynamic_inputs[name] = is_key

    def iter_config_fields(self) -> Iterable[str]:
        """
        Iterate config field names
        """
        if hasattr(self, "config_cls"):
            yield from self.config_cls_slot.__slots__

    def get_initial_inputs(self) -> Dict[str, ValueType]:
        """
        Get dictionary of pre-set inputs and their values

        :return: Dict of initial inputs' values
        """
        if self.const_inputs:
            return self.const_inputs.copy()  # Clone predefined
        return {}  # Nothing set yet

    def freeze(self) -> None:
        """
        Freeze the node and reduce memory footprint.
        No further graph construction manipulations are possible after
        the freezing.
        """
        self.description = None
        self.bound_inputs = None  # Only for charting purposes
