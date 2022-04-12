# ---------------------------------------------------------------------
# MetricAction model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
from typing import Any, Dict

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    ListField,
    EmbeddedDocumentField,
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
from .metrictype import MetricType
from noc.fm.models.alarmclass import AlarmClass


class InputMapping(EmbeddedDocument):
    metric_type = PlainReferenceField(MetricType)
    input_name = StringField(default="in")

    @property
    def json_data(self) -> Dict[str, Any]:
        return {"metric_type__name": self.metric_type.name, "input_name": self.input_name}


class AlarmConfig(EmbeddedDocument):
    alarm_class = PlainReferenceField(AlarmClass)
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
        return {
            "window_function": self.window_function,
            "window_type": self.window_type,
            "window_config": self.window_config,
            "min_window": self.min_window,
            "max_window": self.max_window,
            "activation_function": self.activation_function,
            "activation_config": self.activation_config,
        }


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
    compose_inputs = ListField(EmbeddedDocumentField(InputMapping))
    compose_function = StringField(choices=["sum", "avg", "div"])
    compose_metric_type = PlainReferenceField(MetricType)
    #
    activation_config = EmbeddedDocumentField(ActivationConfig)
    deactivation_config = EmbeddedDocumentField(ActivationConfig)
    #
    key_function = StringField(choices=["disable", "key"])
    alarm_config = EmbeddedDocumentField(AlarmConfig)

    def __str__(self) -> str:
        return self.name

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "metric_type__name": self.metric_type.name,
            "actions": [a.json_data for a in self.actions],
        }
        if self.description:
            r["description"] = self.description
        if self.params:
            r["params"] = [v.json_data for v in self.params]
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=["name", "$collection", "uuid", "description", "metric_type__name", "actions"],
        )

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"
