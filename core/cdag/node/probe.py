# ----------------------------------------------------------------------
# ProbeNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Dict, Callable
from threading import Lock
import inspect

# Third-party modules
from pydantic import BaseModel

# NOC modules
from noc.core.expr import get_fn
from .base import BaseCDAGNode, ValueType, Category

MAX31 = 0x7FFFFFFF
MAX32 = 0xFFFFFFFF
MAX64 = 0xFFFFFFFFFFFFFFFF
NS = 1_000_000_000


class ProbeNodeState(BaseModel):
    lt: Optional[int] = None
    lv: Optional[ValueType] = None


class ProbeNodeConfig(BaseModel):
    unit: str


class ProbeNode(BaseCDAGNode):
    """
    Entrance for collected metrics. Accepts timestamp, value and measurement units.
    Converts counter when necessary
    """

    name = "probe"
    config_cls = ProbeNodeConfig
    state_cls = ProbeNodeState
    categories = [Category.UTIL]
    dot_shape = "cds"
    _conversions: Dict[str, Dict[str, Callable]] = {}
    _conv_lock = Lock()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.convert = self.get_convert(self.config.unit)

    def get_value(self, x: ValueType, ts: int, unit: str) -> Optional[ValueType]:
        # No translation
        if unit == self.config.unit:
            return x
        fn = self.convert[unit]
        kwargs = {}
        if fn.has_x:
            kwargs["x"] = x
        if not (fn.has_delta or fn.has_time_delta):
            # No state dependency, just conversion
            self.set_state(None, None)
            return fn(**kwargs)
        if self.state.lt is None:
            # No previous measurement, store state and exit
            self.set_state(ts, x)
            return None
        if ts <= self.state.lt:
            # Timer stepback, reset state and exit
            self.set_state(None, None)
            return None
        if fn.has_time_delta:
            kwargs["time_delta"] = (ts - self.state.lt) // NS  # Always positive
        if fn.has_delta:
            delta = self.get_delta(x, ts)
            if delta is None:
                # Malformed data, skip
                self.set_state(None, None)
                return None
            kwargs["delta"] = delta
        self.set_state(ts, x)
        return fn(**kwargs)

    def set_state(self, lt, lv):
        self.state.lt = lt
        self.state.lv = lv

    @staticmethod
    def get_bound(v: int) -> int:
        """
        Detect wrap bound
        :param v:
        :return:
        """
        if v <= MAX31:
            return MAX31
        if v <= MAX32:
            return MAX32
        return MAX64

    def get_delta(self, value: ValueType, ts: int) -> Optional[ValueType]:
        """
        Calculate value from delta, gently handling overflows
        :param value:
        :param ts:
        """
        dv = value - self.state.lv
        if dv >= 0:
            self.state.lt = ts
            self.state.lv = value
            return dv
        # Counter wrapped, either due to wrap or due to stepback
        bound = self.get_bound(self.state.lv)
        # Wrap distance
        d_wrap = value + (bound - self.state.lv)
        if -dv < d_wrap:
            # Possible counter stepback, skip value
            return None
        # Counter wrap
        self.state.lt = ts
        self.state.lv = value
        return d_wrap

    @classmethod
    def get_convert(cls, unit: str) -> Dict[str, Callable]:
        def q(expr: str) -> Callable:
            fn = get_fn(expr)
            params = inspect.signature(fn).parameters
            fn.has_x = "x" in params
            fn.has_delta = "delta" in params
            fn.has_time_delta = "time_delta" in params
            return fn

        # Lock-free positive case
        if unit in cls._conversions:
            return cls._conversions[unit]
        # Not ready, try with lock
        with cls._conv_lock:
            # Already prepared by concurrent thread
            if unit in cls._conversions:
                return cls._conversions[unit]
            # Prepare, while concurrent threads are waiting on lock
            cls._conversions[unit] = {u: q(x) for u, x in MS_CONVERT[unit].items()}
            return cls._conversions[unit]


MS_CONVERT = {
    # Name -> alias -> expr
    "bit": {"byte": "x * 8"},
    "bit/s": {"byte/s": "x * 8", "bit": "delta / time_delta", "byte": "delta * 8 / time_delta"},
}
