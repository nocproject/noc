# ---------------------------------------------------------------------
# MetricRule model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, BooleanField, ListField, EmbeddedDocumentField

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from .metrictype import MetricType


class InputMapping(EmbeddedDocument):
    metric_type = PlainReferenceField(MetricType)
    input_name = StringField()


class MetricRuleAction(EmbeddedDocument):
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
    compose_config = StringField()  # JSON
    compose_inputs = ListField(EmbeddedDocumentField(InputMapping))
    compose_metric_type = PlainReferenceField(MetricType)  # Optional metric type, when to store
    # Optional activation node, may be empty
    activation_node = StringField()
    activation_config = StringField()  # JSON
    # Control part, takes activation input
    alarm_node = StringField()
    alarm_config = StringField()  # JSON


class MetricRule(Document):
    meta = {"collection": "metricrules", "strict": False, "auto_create_index": False}
    name = StringField(unique=True)
    is_active = BooleanField(default=True)
    description = StringField()
    # Matching part
    metric_type = PlainReferenceField(MetricType)
    labels = ListField(StringField())
    # List of actions
    actions = ListField(EmbeddedDocumentField(MetricRuleAction))

    def __str__(self) -> str:
        return self.name
