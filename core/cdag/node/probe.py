# ----------------------------------------------------------------------
# ProbeNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Dict, Callable, Iterable, Tuple
from threading import Lock
import inspect
import logging

# Third-party modules
from pydantic import BaseModel

# NOC modules
from noc.core.expr import get_fn
from noc.pm.models.measurementunits import MeasurementUnits
from noc.pm.models.scale import Scale
from .base import BaseCDAGNode, ValueType, Category

MAX31 = 0x7FFFFFFF
MAX32 = 0xFFFFFFFF
MAX64 = 0xFFFFFFFFFFFFFFFF
NS = 1_000_000_000

logger = logging.getLogger(__name__)


class ProbeNodeState(BaseModel):
    lt: Optional[int] = None
    lv: Optional[ValueType] = None
    flag: Optional[int] = None


class ProbeNodeConfig(BaseModel):
    unit: str
    is_delta: bool = False
    scale: str = "1"


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
    _scales: Dict[str, Tuple[int, int]] = {}
    _conv_lock = Lock()
    # Test stub, set by .set_convert() classmethod
    _MS_CONVERT: Dict[str, Dict[str, str]] = {}
    # Test stub, set by .set_scale() classmethod
    _SCALE: Dict[str, Tuple[int, int]] = {}

    __slots__ = "convert", "base", "exp"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.convert = self.get_convert(self.config.unit, self.config.is_delta)
        self.base, self.exp = self.get_scale(self.config.scale)

    def __str__(self):
        return f"{self.name}: {self.node_id}"

    def _upscale(self, v: ValueType, scale: str) -> Optional[ValueType]:
        if v is None:
            return None  # Cannot scale None
        if scale == self.config.scale:
            return v  # No upscale
        base, exp = self.get_scale(scale)
        if base == self.base:
            # Same base
            return v * base ** (exp - self.exp)
        elif self.exp == 0:
            # Base mismatch, Target scale is 1
            return v * base**exp
        elif exp == 0:
            # Base mismatch, Source scale is 1
            return v * self.base**-self.exp
        return v * (base**exp) * self.base**-self.exp

    def get_value(self, x: ValueType, ts: int, unit: str) -> Optional[ValueType]:
        flag = None
        if "|" in unit:
            # <unit>|<flag>
            unit, flag = unit.rsplit("|", 1)
            flag = int(flag)
        if "," in unit:
            # <scale>,<unit>
            scale, unit = unit.split(",")
        else:
            scale = "1"
        # No translation
        if unit == self.config.unit and not self.config.is_delta:
            return self._upscale(x, scale)
        # No conversation. Skipping
        if unit not in self.convert:
            logger.warning(
                "[%s] Not conversation rule from unit %s to %s",
                self.node_id,
                unit,
                self.config.unit,
            )
            return None
        fn = self.convert[unit]
        kwargs = {}
        if fn.has_x:
            kwargs["x"] = x
        if not (fn.has_delta or fn.has_time_delta):
            # No state dependency, just conversion
            self.set_state(None, None)
            return self._upscale(fn(**kwargs), scale)
        if self.state.lt is None:
            # No previous measurement, store state and exit
            self.set_state(ts, x)
            return None
        if ts <= self.state.lt:
            # Timer stepback, reset state and exit
            self.set_state(None, None)
            logger.debug("[%s] Timer StepBack. Reset State and exit", self.node_id)
            return None
        if flag != self.state.flag:
            # Flag is not equal, values is not compared
            logger.info("[%s] Reset flag detected. Skipping value: %s|%s", self.node_id, x, ts)
            self.set_state(None, None)
            self.state.flag = flag
            return None
        elif (ts - self.state.lt) < NS:
            # Too less timestamp different, Division by zero exception
            logger.info("[%s] Skipping already processed value", self.node_id)
            return None
        if fn.has_time_delta:
            kwargs["time_delta"] = (ts - self.state.lt) // NS  # Always positive
        if fn.has_delta:
            delta = self.get_delta(x, ts)
            if delta is None:
                # Malformed data, skip
                self.set_state(None, None)
                logger.debug("[%s] Malformed data, skip", self.node_id)
                return None
            kwargs["delta"] = delta
            if fn.has_x and self.config.is_delta:
                # For other conversation
                kwargs["x"] = delta
        self.set_state(ts, x)
        return self._upscale(fn(**kwargs), scale)

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
    def get_convert(cls, unit: str, is_delta: bool = False) -> Dict[str, Callable]:
        def q(expr: str) -> Callable:
            fn = get_fn(expr)
            params = inspect.signature(fn).parameters
            fn.has_x = "x" in params
            fn.has_delta = "delta" in params or is_delta
            fn.has_time_delta = "time_delta" in params
            return fn

        # Lock-free positive case
        if (unit, is_delta) in cls._conversions:
            return cls._conversions[(unit, is_delta)]
        # Not ready, try with lock
        with cls._conv_lock:
            # Already prepared by concurrent thread
            if (unit, is_delta) in cls._conversions:
                return cls._conversions[(unit, is_delta)]
            # Prepare, while concurrent threads are waiting on lock
            cls._conversions[(unit, is_delta)] = {u: q(x) for u, x in cls.iter_conversion(unit)}
            if is_delta:
                cls._conversions[(unit, is_delta)][unit] = q("delta")
            return cls._conversions[(unit, is_delta)]

    @classmethod
    def get_scale(cls, code: str) -> Tuple[int, int]:
        """
        Get scale base and exponent by code
        :param code: Scale code
        :return: Tuple of base, exp
        """
        # Lock-free positive case
        x = cls._scales.get(code)
        if x:
            return x
        # Not ready, try with lock
        with cls._conv_lock:
            # Already prepared by concurrent thread
            if code in cls._scales:
                return cls._scales[code]
            # Prepare, while concurrent threads waiting on lock
            cls._scales = {s_code: (s_base, s_exp) for s_code, s_base, s_exp in cls.iter_scales()}
            return cls._scales[code]

    @classmethod
    def iter_conversion(cls, code: str) -> Iterable[Tuple[str, str]]:
        """
        Iterate all possible conversions for unit code
        :param code:
        :return:
        """
        if cls._MS_CONVERT:
            # Test branch
            yield from cls._MS_CONVERT[code].items()
        else:
            # Real path
            mu = MeasurementUnits.get_by_code(code)
            if mu and mu.convert_from:
                for conv in mu.convert_from:
                    yield conv.unit.code, conv.expr

    @classmethod
    def iter_scales(cls) -> Iterable[Tuple[str, int, int]]:
        if cls._SCALE:
            # Test branch
            for code, (base, exp) in cls._SCALE.items():
                yield code, base, exp
        else:
            # Real path
            for scale in Scale.objects.all():
                yield scale.code, scale.base, scale.exp

    @classmethod
    def set_convert(cls, data: Dict[str, Dict[str, str]]) -> None:
        """
        Override database-based measure units by test data
        :param data:
        :return:
        """
        cls._MS_CONVERT = data

    @classmethod
    def reset_convert(cls):
        """
        Remove conversion override set by .set_convert()
        :return:
        """
        cls._MS_CONVERT = {}

    @classmethod
    def set_scale(cls, data: Dict[str, Tuple[int, int]]) -> None:
        """
        Override database-based scales by test data
        :param data:
        :return:
        """
        cls._SCALE = data

    @classmethod
    def reset_scale(cls):
        """
        Remove scale-based override set by .set_scale()
        :return:
        """
        cls._SCALE = {}

    def get_time_delta(self, ts: int) -> Optional[int]:
        """
        Calculate time_delta from node ts
        return
        """
        if not self.state.lt:
            return None
        return abs(int((ts - self.state.lt) / NS))
