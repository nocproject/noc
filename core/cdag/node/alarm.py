# ----------------------------------------------------------------------
# Alarm node
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import datetime
from typing import Optional, List

# Third-party modules
from pydantic import BaseModel
import orjson
from jinja2 import Template

# NOC modules
from .base import BaseCDAGNode, ValueType, Category
from noc.core.service.loader import get_service


class AlarmNodeState(BaseModel):
    active: bool = False
    last_raise: datetime.datetime = None


class VarItem(BaseModel):
    name: str
    value: str


class AlarmNodeConfig(BaseModel):
    alarm_class: str
    reference: Optional[str] = None
    dry_run: bool = False  # For service test used
    pool: str = ""
    partition: int = 0
    managed_object: Optional[str] = None  # Not user-settable
    sla_probe: Optional[str] = None  # Not user-settable
    sensor: Optional[str] = None  # Not user-settable
    service: Optional[str] = None  # Not user-settable
    labels: Optional[List[str]] = None
    error_text_template: Optional[str] = None
    activation_level: float = 1.0
    deactivation_level: float = 1.0
    invert_condition: bool = False
    vars: Optional[List[VarItem]]

    @classmethod
    def get_reference(cls, config: "AlarmNodeConfig") -> str:
        """
        Create Alarm reference by config
        :param config: Alarm Config
        :return:
        """
        template = "th:{{object}}:{{alarm_class}}"
        if config.reference:
            template = config.reference
        elif config.labels:
            template = "th:{{object or ''}}:{{alarm_class}}:{{';'.join(config.labels)}}"
        return Template(template).render(
            **{
                "object": config.managed_object,
                "alarm_class": config.alarm_class,
                "labels": config.labels or [],
                "vars": {v.name: v.value for v in config.vars or []},
            }
        )


logger = logging.getLogger(__name__)


class AlarmNode(BaseCDAGNode):
    """
    Maintain alarm state
    """

    name = "alarm"
    config_cls = AlarmNodeConfig
    state_cls = AlarmNodeState
    categories = [Category.UTIL]

    def get_value(self, x: ValueType, **kwargs) -> Optional[ValueType]:
        """
        * If x - check activate
        :param x: Activate input
        :param kwargs: Deactivate input
        :return:
        """
        if self.state.active and (
            (not self.config.invert_condition and x < self.config.deactivation_level)
            or (self.config.invert_condition and x > self.config.deactivation_level)
        ):
            self.clear_alarm()
        elif not self.state.active and (
            (not self.config.invert_condition and x >= self.config.activation_level)
            or (self.config.invert_condition and x <= self.config.activation_level)
        ):
            self.raise_alarm(x)
        return None

    def raise_alarm(self, x: ValueType) -> None:
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
            "alarm_class": self.config.alarm_class,
            "labels": list(self.config.labels or []),
            # x is numpy.float64 type, ?
            "vars": {
                "ovalue": round(float(x), 3),
                "tvalue": self.config.activation_level,
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
        self.state.active = True
        self.state.last_raise = now.replace(microsecond=0)
        logger.info(
            "[%s|%s|%s|%s] Raise alarm: %s",
            self.node_id,
            self.config.managed_object,
            ";".join(self.config.labels or []),
            self.config.pool,
            x,
        )

    def clear_alarm(self, message: Optional[str] = None) -> None:
        """
        Clear alarm
        """
        msg = {
            "$op": "clear",
            "reference": self.config_cls.get_reference(self.config),
            "timestamp": datetime.datetime.now().isoformat(),
            "message": message,
        }
        self.publish_message(msg)
        self.state.active = False
        logger.info(
            "[%s|%s|%s] Clear alarm",
            self.node_id,
            self.config.managed_object,
            ";".join(self.config.labels or []),
        )

    def publish_message(self, msg):
        if self.config.dry_run or not self.config.pool:
            return
        svc = get_service()
        svc.publish(
            orjson.dumps(msg), stream=f"dispose.{self.config.pool}", partition=self.config.partition
        )

    def is_active(self) -> bool:
        return self.state.active

    def reset_state(self):
        """
        Reset Alarm Node state
        :return:
        """
        if not self.is_active():
            return
        self.clear_alarm("Reset by change node config")
        self.state.active = False

    def is_required_input(self, name: str) -> bool:
        """
        If set deactivate_x Input, used it for check deactivate_level
        :param name:
        :return:
        """
        if self.state.active and self.dynamic_inputs and name == "deactivate_x":
            return True
        return super().is_required_input(name)

    def __del__(self):
        self.reset_state()
