# ---------------------------------------------------------------------
# MetricAction model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
from typing import Any, Dict, List

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    ListField,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    UUIDField,
    DictField,
    FloatField,
    IntField,
)

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from noc.core.model.decorator import on_delete_check
from noc.fm.models.alarmclass import AlarmClass
from noc.pm.models.metrictype import MetricType
from noc.sa.interfaces.base import (
    StringParameter,
    IntParameter,
    BooleanParameter,
    FloatParameter,
    Parameter,
)

TYPE_MAP: Dict[str, Parameter] = {
    "str": StringParameter(),
    "int": IntParameter(),
    "float": FloatParameter(),
    "bool": BooleanParameter(),
}


class MetricActionParam(EmbeddedDocument):
    meta = {"strict": False}
    name = StringField()
    type = StringField(choices=["str", "int", "bool", "float"], default="int")
    min_value = FloatField()
    max_value = FloatField()
    default = StringField()
    description = StringField()

    def __str__(self):
        return f"{self.name} ({self.type})"

    @property
    def json_data(self):
        return {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "min_value": self.min_value,
            "max_value": self.min_value,
            "default": self.default,
        }

    def clean_value(self, value):
        validator = TYPE_MAP[self.type]
        if hasattr(validator, "min_value") and self.min_value:
            setattr(validator, "min_value", self.min_value)
        if hasattr(validator, "max_value") and self.max_value:
            setattr(validator, "max_value", self.max_value)
        return validator.clean(value)


class InputMapping(EmbeddedDocument):
    metric_type: "MetricType" = PlainReferenceField(MetricType)
    input_name = StringField(default="in")

    @property
    def json_data(self) -> Dict[str, Any]:
        return {"metric_type__name": self.metric_type.name, "input_name": self.input_name}


class AlarmConfig(EmbeddedDocument):
    alarm_class: "AlarmClass" = PlainReferenceField(AlarmClass)
    reference = StringField()
    activation_level = FloatField(default=1.0)
    deactivation_level = FloatField(default=1.0)
    vars = DictField()

    @property
    def json_data(self) -> Dict[str, Any]:
        return {
            "alarm_class": self.alarm_class.name,
            "reference": self.reference,
            "activation_level": self.activation_level,
            "deactivation_level": self.deactivation_level,
        }


class ActivationConfig(EmbeddedDocument):
    window_function = StringField(
        choices=["percentile", "nth", "expdecay", "sumstep"], default=None
    )
    # Tick, Seconds
    window_type = StringField(choices=["tick", "seconds"], default="tick")
    window_config = DictField()
    min_window = IntField(default=1)
    max_window = IntField(default=1)
    activation_function = StringField(choices=["relu", "logistic", "indicator", "softplus"])
    activation_config = DictField()

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {}
        if self.window_function:
            r.update(
                {
                    "window_function": self.window_function,
                    "window_type": self.window_type,
                    "window_config": self.window_config,
                    "min_window": self.min_window,
                    "max_window": self.max_window,
                }
            )
        if self.activation_function:
            r.update(
                {
                    "activation_function": self.activation_function,
                    "activation_config": self.activation_config,
                }
            )
        return r


@on_delete_check(check=[("pm.MetricRule", "items.metric_action")])
class MetricAction(Document):
    meta = {
        "collection": "metricactions",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "pm.metricactions",
        "json_unique_fields": ["name"],
    }
    name = StringField(unique=True)
    uuid = UUIDField(binary=True)
    description = StringField()
    #
    params: List["MetricActionParam"] = EmbeddedDocumentListField(MetricActionParam)
    #
    compose_inputs: List["InputMapping"] = ListField(EmbeddedDocumentField(InputMapping))
    compose_function: str = StringField(choices=["sum", "avg", "div"], default=None)
    compose_metric_type: "MetricType" = PlainReferenceField(MetricType)
    #
    activation_config: ActivationConfig = EmbeddedDocumentField(ActivationConfig)
    deactivation_config: ActivationConfig = EmbeddedDocumentField(ActivationConfig)
    #
    key_function: str = StringField(choices=["key"], default=None)
    alarm_config: "AlarmConfig" = EmbeddedDocumentField(AlarmConfig)

    def __str__(self) -> str:
        return self.name

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "params": [p.json_data for p in self.params],
            "compose_inputs": [ci.json_data for ci in self.compose_inputs],
        }
        if self.description:
            r["description"] = self.description
        if self.compose_function:
            r["compose_function"] = self.compose_function
        if self.activation_config.window_function or self.activation_config.activation_function:
            r["activation_config"] = self.activation_config.json_data
        if self.deactivation_config.window_function or self.deactivation_config.activation_function:
            r["deactivation_config"] = self.deactivation_config.json_data
        if self.key_function:
            r["key_function"] = self.key_function
        if self.alarm_config:
            r["alarm_config"] = self.alarm_config.json_data
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=["name", "$collection", "uuid", "description", "params", "compose_inputs"],
        )

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"
