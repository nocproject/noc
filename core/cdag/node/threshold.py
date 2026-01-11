# ----------------------------------------------------------------------
# Threshold node
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
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
from noc.core.service.loader import get_service


class ThresholdState(BaseModel):
    active: bool = False
    reference: str = None
    pool: Optional[str] = None
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

        if self.clear_value is None:
            return (
                (self.op == "<" and value >= self.value)
                or (self.op == "<=" and value > self.value)
                or (self.op == ">=" and value < self.value)
                or (self.op == ">" and value <= self.value)
            )
        return (
            (self.op == "<" and value >= self.clear_value)
            or (self.op == "<=" and value > self.clear_value)
            or (self.op == ">=" and value < self.clear_value)
            or (self.op == ">" and value <= self.clear_value)
        )


class ThresholdNodeConfig(BaseModel):
    alarm_class: Optional[str] = None
    reference: Optional[str] = None
    error_text_template: Optional[str] = None
    vars: Optional[List[VarItem]] = None
    pool: str = ""
    dry_run: bool = False  # For service test used
    partition: int = 0
    rule_id: str
    action_id: str
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

    @property
    def rule_id(self) -> str:
        return f"{self.config.rule_id}-{self.config.action_id}"

    def iter_thresholds(self) -> Iterable[ThresholdItem]:
        for num, th in enumerate(ta_ListThresholdItem.validate_python(self.config.thresholds)):
            yield num, th

    # check pool
    def get_value(self, x: ValueType, target: Any, **kwargs):
        logger.debug("[%s] Getting threshold value: %s", target, x)
        for num, th in self.iter_thresholds():
            if self.is_active(str(num)) and th.is_clear_match(x):
                self.clear_alarm(str(num))
            elif th.is_open_match(x) and not self.is_active(str(num)):
                self.raise_alarm(x, target, th, str(num))

    def get_reference(self, th: ThresholdItem, target: Any) -> str:
        """Create Alarm reference by config"""
        template = "th:{{object}}:{{alarm_class}}"
        if self.config.reference:
            template = self.config.reference
        elif th.alarm_labels:
            template = "th:{{object or ''}}:{{alarm_class}}:{{';'.join(labels)}}"
        return Template(template).render(
            **{
                "object": target.managed_object,
                "alarm_class": th.alarm_class,
                "labels": th.alarm_labels or [],
                "vars": {v.name: v.value for v in self.config.vars or []},
            }
        )

    def raise_alarm(self, x: ValueType, target, th: ThresholdItem = None, tid: str = None) -> None:
        """
        Raise alarm
        """

        logger.info("[%s] Raise Alarm", th)
        now = datetime.datetime.now().replace(microsecond=0)
        msg = {
            "$op": "raise",
            "reference": self.get_reference(th, target),
            "timestamp": now.isoformat(),
            "managed_object": f"bi_id:{target.managed_object}",
            "alarm_class": th.alarm_class,
            "labels": th.alarm_labels or [],
            "vars": {
                "ovalue": round(float(x), 3),
                "tvalue": th.value,
                "node_id": self.node_id,
            },
        }
        # Render vars
        if self.config.vars:
            msg["vars"].update({v.name: v.value for v in self.config.vars})
        if self.config.error_text_template:
            msg["vars"]["message"] = self.config.error_text_template
        if target.type == "sla_probe":
            msg["vars"]["sla_probe"] = target.bi_id
            if target.service:
                msg["vars"]["service"] = target.service
        if target.type == "sensor":
            msg["vars"]["sensor"] = target.bi_id
        self.publish_message(msg, target.fm_pool)
        self.set_state(tid, reference=self.get_reference(th, target), pool=target.fm_pool)
        logger.info(
            "[%s|%s|%s|%s] Raise alarm: %s",
            self.node_id,
            target.managed_object,
            ";".join(th.alarm_labels or []),
            target.fm_pool,
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
        self.publish_message(msg, self.state.thresholds[threshold].pool)
        self.state.thresholds[threshold].active = False
        logger.info(
            "[%s|%s|%s] Clear alarm",
            self.node_id,
            threshold,
            "",
        )

    def is_active(self, threshold: Optional[str] = None) -> bool:
        if threshold and threshold in self.state.thresholds:
            return self.state.thresholds[threshold].active
        if threshold:
            return False
        return any(t.active for t in self.state.thresholds.values())

    def set_state(
        self, threshold: str, reference: Optional[str] = None, pool: Optional[str] = None
    ):
        if threshold in self.state.thresholds:
            self.state.thresholds[threshold].active = True
            self.state.thresholds[threshold].last_raise = datetime.datetime.now().replace(
                microsecond=0
            )
            self.state.thresholds[threshold].reference = reference
            self.state.thresholds[threshold].pool = pool
        else:
            self.state.thresholds[threshold] = ThresholdState(
                active=True,
                last_raise=datetime.datetime.now(),
                reference=reference,
                pool=pool,
            )

    def reset_state(self, threshold: Optional[str] = None):
        """Reset Alarm Node state"""
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

    def publish_message(self, msg, pool: str):
        if self.config.dry_run or not pool:
            return
        svc = get_service()
        svc.publish(orjson.dumps(msg), stream=f"dispose.{pool}", partition=self.config.partition)

    def __del__(self):
        self.reset_state()

    def clean_state(self, state: Optional[Dict[str, Any]]) -> Optional[BaseModel]:
        if not hasattr(self, "state_cls"):
            return None
        state = state or {}
        return self.state_cls(**state)
