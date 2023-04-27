# ----------------------------------------------------------------------
# Threshold node
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional, List, Dict, Literal

# Third-party modules
from pydantic import BaseModel

# NOC modules
from .base import ValueType
from .alarm import AlarmNode, AlarmNodeConfig


class ThresholdState(BaseModel):
    active: bool = False
    last_raise: datetime.datetime = None


class ThresholdNodeState(BaseModel):
    thresholds: Dict[str, ThresholdState] = {}

    def is_active(self, threshold: str) -> bool:
        if threshold in self.thresholds:
            return self.thresholds[threshold].active
        return False

    def set_state(self, threshold: str):
        if threshold in self.thresholds:
            self.thresholds[threshold].active = True
            self.thresholds[threshold].last_raise = datetime.datetime.now()
        else:
            self.thresholds[threshold] = ThresholdState(
                active=True, last_raise=datetime.datetime.now()
            )

    def reset_state(self, threshold):
        if threshold in self.thresholds:
            self.thresholds[threshold].active = False


class VarItem(BaseModel):
    name: str
    value: str


class ThresholdItem(BaseModel):
    value: float = 1
    op: Literal[">", ">=", "<", "<="] = ">="
    clear_value: Optional[float] = None
    alarm_class: Optional[str] = None
    alarm_labels: Optional[List[str]] = None

    def is_open_match(self, value: ValueType) -> bool:
        """
        Check if threshold profile is matched for open condition
        :param value:
        :return:
        """
        return (
            (self.op == "<" and value < self.value)
            or (self.op == "<=" and value <= self.value)
            or (self.op == ">=" and value >= self.value)
            or (self.op == ">" and value > self.value)
        )

    def is_clear_match(self, value: ValueType) -> bool:
        """
        Check if threshold profile is matched for clear condition
        :param value:
        :return:
        """
        if (self.clear_value and value < self.clear_value) or value < self.value:
            return True
        return False


class ThresholdNodeConfig(AlarmNodeConfig):
    alarm_class: Optional[str] = "NOC | PM | Out of Thresholds"
    thresholds: List[ThresholdItem]


class ThresholdNode(AlarmNode):
    """
    Maintain Thresholds
    """

    name = "threshold"
    config_cls = ThresholdNodeConfig
    state_cls = ThresholdNodeState

    def get_value(self, x: ValueType, **kwargs):
        for num, th in enumerate(self.config.thresholds):
            if self.state.is_active(th.value) and th.is_clear_match(x):
                self.clear_alarm()
            elif th.is_open_match(x) and not self.state.is_active(th.value):
                self.raise_alarm(x, th.labels)
