# ----------------------------------------------------------------------
# Alarm node
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import datetime
from typing import Optional, List, Any

# Third-party modules
from pydantic import BaseModel
import orjson
from jinja2 import Template

# NOC modules
from .base import BaseCDAGNode, ValueType, Category
from noc.core.service.loader import get_service


class AlarmNodeState(BaseModel):
    active: bool = False
    pool: Optional[str] = None
    reference: Optional[str] = None
    last_raise: datetime.datetime = None


class VarItem(BaseModel):
    name: str
    value: str


class AlarmNodeConfig(BaseModel):
    alarm_class: str
    rule_id: str
    action_id: str
    reference: Optional[str] = None
    dry_run: bool = False  # For service test used
    pool: str = ""
    partition: int = 0
    labels: Optional[List[str]] = None
    error_text_template: Optional[str] = None
    activation_level: float = 1.0
    deactivation_level: float = 1.0
    invert_condition: bool = False
    vars: Optional[List[VarItem]] = None


logger = logging.getLogger(__name__)


class AlarmNode(BaseCDAGNode):
    """
    Maintain alarm state
    """

    name = "alarm"
    config_cls = AlarmNodeConfig
    state_cls = AlarmNodeState
    categories = [Category.UTIL]

    @property
    def rule_id(self) -> str:
        return f"{self.config.rule_id}-{self.config.action_id}"

    def get_value(self, x: ValueType, target: Any, **kwargs) -> Optional[ValueType]:
        """
        * If x - check activate
        Args:
            x: Activate input
            target:
            kwargs: Deactivate input
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
            self.raise_alarm(x, target)
        return None

    def get_reference(self, managed_object) -> str:
        """
        Create Alarm reference by config
        Args:
            managed_object: Alarm Config
        """
        template = "th:{{object}}:{{alarm_class}}"
        if self.config.reference:
            template = self.config.reference
        elif self.config.labels:
            template = "th:{{object or ''}}:{{alarm_class}}:{{';'.join(labels)}}"
        return Template(template).render(
            **{
                "object": managed_object,
                "alarm_class": self.config.alarm_class,
                "labels": self.config.labels or [],
                "vars": {v.name: v.value for v in self.config.vars or []},
            }
        )

    def raise_alarm(self, x: ValueType, target) -> None:
        """
        Raise alarm
        """

        def q(v):
            template = Template(v)
            return template.render(x=x, config=self.config)

        now = datetime.datetime.now()
        ref = self.get_reference(target.managed_object)
        msg = {
            "$op": "raise",
            "reference": ref,
            "timestamp": now.isoformat(),
            "managed_object": target.managed_object,
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
        if target.type == "sla_probe":
            msg["vars"]["sla_probe"] = target.bi_id
            if target.service:
                msg["vars"]["service"] = target.service
        if target.type == "sensor":
            msg["vars"]["sensor"] = target.bi_id
        self.publish_message(msg, pool=target.fm_pool)
        self.state.active = True
        self.state.reference = ref
        self.state.last_raise = now.replace(microsecond=0)
        logger.info(
            "[%s|%s|%s|%s] Raise alarm: %s",
            self.node_id,
            target.managed_object,
            ";".join(self.config.labels or []),
            target.fm_pool or self.config.pool,
            x,
        )

    def clear_alarm(self, message: Optional[str] = None) -> None:
        """
        Clear alarm
        """
        msg = {
            "$op": "clear",
            "reference": self.state.reference,
            "timestamp": datetime.datetime.now().isoformat(),
            "message": message,
        }
        self.publish_message(msg, self.state.pool or self.config.pool)
        logger.info(
            "[%s|%s|%s] Clear alarm",
            self.node_id,
            # self.config.managed_object,
            self.state.reference,
            ";".join(self.config.labels or []),
        )
        self.state.active = False
        self.state.reference = None

    def publish_message(self, msg, pool: str):
        if self.config.dry_run or not self.config.pool:
            return
        svc = get_service()
        svc.publish(orjson.dumps(msg), stream=f"dispose.{pool}", partition=self.config.partition)

    def is_active(self) -> bool:
        return self.state.active

    def reset_state(self):
        """Reset Alarm Node state"""
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
