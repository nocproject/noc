# ----------------------------------------------------------------------
# WindowNode base
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List
from enum import Enum
from time import time_ns

# Third-party modules
from pydantic import BaseModel

# NOC modules
from ..typing import ValueType, StrictValueType
from .base import BaseCDAGNode, Category

NS = 1_000_000_000


class WindowType(str, Enum):
    TICKS = "t"
    SECONDS = "s"


class WindowNodeState(BaseModel):
    timestamps: List[int] = []
    values: List[StrictValueType] = []


class WindowConfig(BaseModel):
    type: WindowType = WindowType.TICKS
    min_window: int = 1
    max_window: int = 100


class WindowNode(BaseCDAGNode):
    name = "window"
    config_cls = WindowConfig
    state_cls = WindowNodeState
    categories = [Category.WINDOW]

    def get_window_value(
        self, values: List[ValueType], timestamps: List[int]
    ) -> Optional[ValueType]:  # pragma: no cover
        raise NotImplementedError

    def is_filled_ticks(self) -> bool:
        """
        Check window has enough ticks
        :return:
        """
        return len(self.state.values) >= self.config.min_window

    def is_filled_seconds(self, ts: int) -> bool:
        """
        Check window has enough seconds
        :return:
        """
        return (
            bool(self.state.timestamps)
            and (ts - self.state.timestamps[0]) >= self.config.min_window * NS
        )

    def trim_ticks(self) -> None:
        del self.state.values[: -self.config.max_window]
        del self.state.timestamps[: -self.config.max_window]

    def trim_seconds(self, ts: int) -> None:
        n = 0
        deadline = ts - self.config.max_window * NS
        for t in self.state.timestamps:
            if t >= deadline:
                break
            n += 1
        if n:
            del self.state.values[:n]
            del self.state.timestamps[:n]

    def push(self, ts: int, value: ValueType) -> None:
        self.state.values.append(value)
        self.state.timestamps.append(ts)

    def get_value(self, x: ValueType) -> Optional[ValueType]:
        # Fill the window
        ts = time_ns()
        self.push(ts, x)
        is_ticks = self.config.type == WindowType.TICKS
        # Check min requirements
        if self.config.min_window and (
            (is_ticks and not self.is_filled_ticks())
            or (not is_ticks and not self.is_filled_seconds(ts))
        ):
            return self.get_missed_value()
        # Trim window to maximum size
        if is_ticks:
            self.trim_ticks()
        else:
            self.trim_seconds(ts)
        # Calculate value
        return self.get_window_value(self.state.values, self.state.timestamps)

    def get_missed_value(self) -> Optional[ValueType]:
        return None
