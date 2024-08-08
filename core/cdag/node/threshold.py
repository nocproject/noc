# ----------------------------------------------------------------------
# Threshold node
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import logging
from typing import Optional, List, Dict, Literal, Iterable, Any

# Third-party modules
import orjson
from jinja2 import Template
from pydantic import BaseModel, TypeAdapter

# NOC modules
from .base import BaseCDAGNode, ValueType, Category
from .alarm import AlarmNodeConfig
from noc.core.service.loader import get_service


class ThresholdState(BaseModel):
    active: bool = False
    reference: str = None
    last_raise: datetime.datetime = None


class ThresholdNodeState(BaseModel):
    thresholds: Dict[str, ThresholdState] = {}


class VarItem(BaseModel):
    name: str
    value: str


class ThresholdItem(BaseModel):
    value: float = 1
    op: Literal[">", ">=", "<", "<="] = ">="
    clear_value: Optional[float] = None
    alarm_class: Optional[str] = "NOC | PM | Out of Thresholds"
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
    alarm_class: Optional[str] = None
    thresholds: List[ThresholdItem]


logger = logging.getLogger(__name__)
ta_ListThresholdItem = TypeAdapter(List[ThresholdItem])


class ThresholdNode(BaseCDAGNode):
    """
    Maintain Thresholds
    """

    name = "threshold"
    config_cls = ThresholdNodeConfig
    state_cls = ThresholdNodeState
    categories = [Category.UTIL]

    def iter_thresholds(self) -> Iterable[ThresholdItem]:
        for num, th in enumerate(ta_ListThresholdItem.validate_python(self.config.thresholds)):
            yield num, th

    def get_value(self, x: ValueType, **kwargs):
        for num, th in self.iter_thresholds():
            if self.is_active(str(num)) and th.is_clear_match(x):
                self.clear_alarm(str(num))
            elif th.is_open_match(x) and not self.is_active(str(num)):
                self.raise_alarm(x, th, str(num))

    def raise_alarm(self, x: ValueType, th: ThresholdItem = None, tid: str = None) -> None:
        """
        Raise alarm
        """

        def q(v):
            template = Template(v)
            return template.render(x=x, config=self.config)

        now = datetime.datetime.now()
        msg = {
            "$op": "raise",
            "reference": self.config_cls.get_reference(self.config),
            "timestamp": now.isoformat(),
            "managed_object": self.config.managed_object,
            "alarm_class": th.alarm_class,
            "labels": list(self.config.labels or []) + (th.alarm_labels or []),
            # x is numpy.float64 type, ?
            "vars": {
                "ovalue": round(float(x), 3),
                "tvalue": th.value,
                "node_id": self.node_id,
            },
        }
        # Render vars
        if self.config.vars:
            msg["vars"].update({v.name: q(v.value) for v in self.config.vars})
        if self.config.error_text_template:
            msg["vars"]["message"] = self.config.error_text_template
        if self.config.sla_probe:
            msg["vars"]["sla_probe"] = self.config.sla_probe
        if self.config.sensor:
            msg["vars"]["sensor"] = self.config.sensor
        if self.config.service:
            msg["vars"]["service"] = self.config.service
        self.publish_message(msg)
        self.set_state(tid, reference=self.config_cls.get_reference(self.config))
        logger.info(
            "[%s|%s|%s|%s] Raise alarm: %s",
            self.node_id,
            self.config.managed_object,
            ";".join(self.config.labels or []),
            self.config.pool,
            x,
        )

    def clear_alarm(self, threshold: Optional[str] = None, message: Optional[str] = None) -> None:
        """
        Clear alarm
        """
        msg = {
            "$op": "clear",
            "reference": self.state.thresholds[threshold].reference,
            "timestamp": datetime.datetime.now().isoformat(),
            "message": message,
        }
        self.publish_message(msg)
        self.state.thresholds[threshold].active = False
        logger.info(
            "[%s|%s|%s] Clear alarm",
            self.node_id,
            self.config.managed_object,
            ";".join(self.config.labels or []),
        )

    def is_active(self, threshold: Optional[str] = None) -> bool:
        if threshold and threshold in self.state.thresholds:
            return self.state.thresholds[threshold].active
        elif threshold:
            return False
        return any(t.active for t in self.state.thresholds.values())

    def set_state(self, threshold: str, reference: Optional[str] = None):
        if threshold in self.state.thresholds:
            self.state.thresholds[threshold].active = True
            self.state.thresholds[threshold].last_raise = datetime.datetime.now().replace(
                microsecond=0
            )
            self.state.thresholds[threshold].reference = reference
        else:
            self.state.thresholds[threshold] = ThresholdState(
                active=True,
                last_raise=datetime.datetime.now(),
                reference=reference,
            )

    def reset_state(self, threshold: Optional[str] = None):
        """
        Reset Alarm Node state
        :return:
        """
        if not self.is_active(threshold):
            return
        if threshold:
            self.clear_alarm(threshold)
            self.state[threshold].active = False
        for th, state in self.state.thresholds.items():
            if not state.active:
                continue
            self.clear_alarm(th, "Reset by change node config")
            state.active = False

    def publish_message(self, msg):
        if self.config.dry_run or not self.config.pool:
            return
        svc = get_service()
        svc.publish(
            orjson.dumps(msg), stream=f"dispose.{self.config.pool}", partition=self.config.partition
        )

    def __del__(self):
        self.reset_state()

    def clean_state(self, state: Optional[Dict[str, Any]]) -> Optional[BaseModel]:
        if not hasattr(self, "state_cls"):
            return None
        state = state or {}
        c_state = self.state_cls(**state)
        return c_state
