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
)

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from noc.core.model.decorator import on_delete_check
from .metrictype import MetricType


class ActionParam(EmbeddedDocument):
    name = StringField()
    description = StringField()

    @property
    def json_data(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
        }


class InputMapping(EmbeddedDocument):
    metric_type = PlainReferenceField(MetricType)
    input_name = StringField()

    @property
    def json_data(self) -> Dict[str, Any]:
        return {"metric_type__name": self.metric_type.name, "input_name": self.input_name}


class ActionItem(EmbeddedDocument):
    """
    Pipeline:

    ```mermaid
    graph LR
        Metric Type --> Compose
        Compose --> Activation
        Compose --> Sender
        Activation --> Control
    ```

    Each stage may be empty
    """

    # Compose part, may be empty
    compose_node = StringField()  # Type of compose node
    compose_config = DictField()
    compose_inputs = ListField(EmbeddedDocumentField(InputMapping))
    compose_metric_type = PlainReferenceField(MetricType)  # Optional metric type, when to store
    # Optional activation node, may be empty
    activation_node = StringField()
    activation_config = DictField()
    # Control part, takes activation input
    alarm_node = StringField()
    alarm_config = DictField()

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {}
        if self.compose_node:
            r["compose_node"] = self.compose_node
            if self.compose_config:
                r["compose_config"] = self.compose_config
            if self.compose_inputs:
                r["compose_inputs"] = [i.json_data for i in self.compose_inputs]
            if self.compose_metric_type:
                r["compose_metric_type__name"] = self.compose_metric_type.name
        if self.activation_node:
            r["activation_node"] = self.activation_node
            if self.activation_config:
                r["activation_config"] = self.activation_config
        if self.alarm_node:
            r["alarm_node"] = self.alarm_node
            if self.alarm_config:
                r["alarm_config"] = self.alarm_config
        return r


@on_delete_check(check=[("pm.MetricRule", "metric_action")])
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
    metric_type = PlainReferenceField(MetricType)
    actions = ListField(EmbeddedDocumentField(ActionItem))
    params = ListField(EmbeddedDocumentField(ActionParam))

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
