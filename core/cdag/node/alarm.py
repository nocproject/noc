# ----------------------------------------------------------------------
# Alarm node
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List
import datetime

# Third-party modules
from pydantic import BaseModel
import orjson

# NOC modules
from .base import BaseCDAGNode, ValueType, Category
from noc.core.service.loader import get_service


class AlarmNodeState(BaseModel):
    active: bool = False


class AlarmNodeConfig(BaseModel):
    reference: str
    pool: str
    partition: int
    alarm_class: str
    managed_object: str
    labels: Optional[List[str]]
    activation_level: float = 1.0
    deactivation_level: float = 1.0


class AlarmNode(BaseCDAGNode):
    """
    Maintain alarm state
    """

    name = "alarm"
    config_cls = AlarmNodeConfig
    state_cls = AlarmNodeState
    categories = [Category.UTIL]

    def get_value(self, x: ValueType) -> Optional[ValueType]:
        if self.state.active and x < self.config.deactivation_level:
            self.clear_alarm()
        elif not self.state.active and x >= self.config.activation_level:
            self.raise_alarm()
        return None

    def raise_alarm(self):
        """
        Raise alarm
        """
        msg = {
            "$op": "raise",
            "reference": self.config.reference,
            "timestamp": datetime.datetime.now().isoformat(),
            "managed_object": self.config.managed_object,
            "alarm_class": self.config.alarm_class,
            "labels": self.config.labels if self.config.labels else [],
        }
        svc = get_service()
        svc.publish(
            orjson.dumps(msg), stream=f"dispose.{self.config.pool}", partition=self.config.partition
        )
        self.state.active = True

    def clear_alarm(self):
        """
        Clear alarm
        """
        msg = {
            "$op": "clear",
            "reference": self.config.reference,
            "timestamp": datetime.datetime.now().isoformat(),
        }
        svc = get_service()
        svc.publish(
            orjson.dumps(msg), stream=f"dispose.{self.config.pool}", partition=self.config.partition
        )
        self.state.active = False
