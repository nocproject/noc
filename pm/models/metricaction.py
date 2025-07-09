# ---------------------------------------------------------------------
# MetricAction model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
from typing import Any, Dict, Optional, List, Union
from collections import defaultdict

# Third-party modules
from bson import ObjectId
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
    BooleanField,
)
from mongoengine.errors import ValidationError

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from noc.core.model.decorator import on_delete_check
from noc.core.cdag.factory.config import NodeItem, InputItem, GraphConfig
from noc.core.cdag.node.alarm import VarItem
from noc.core.change.decorator import change
from noc.core.expr import get_fn, get_vars
from noc.fm.models.alarmclass import AlarmClass
from noc.pm.models.metrictype import MetricType
from noc.sa.interfaces.base import (
    StringParameter,
    IntParameter,
    BooleanParameter,
    FloatParameter,
    Parameter,
)
from noc.config import config

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
            "max_value": self.max_value,
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
    invert_condition = BooleanField(default=False)
    error_text_template = StringField()
    vars = DictField()

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {}
        if self.alarm_class:
            r["alarm_class__name"] = self.alarm_class.name
        if self.reference:
            r["reference"] = self.reference
        if self.activation_level != 1.0:
            r["activation_level"] = self.activation_level
        if self.deactivation_level != 1.0:
            r["deactivation_level"] = self.deactivation_level
        if self.invert_condition:
            r["invert_condition"] = self.invert_condition
        return r


class ActivationConfig(EmbeddedDocument):
    window_function = StringField(
        choices=["percentile", "nth", "expdecay", "sumstep", "mean"], default=None
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


@change
@on_delete_check(check=[("pm.MetricRule", "actions.metric_action")])
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
    compose_expression = StringField(default=None)
    compose_metric_type: "MetricType" = PlainReferenceField(MetricType)
    #
    activation_config: ActivationConfig = EmbeddedDocumentField(ActivationConfig)
    deactivation_config: ActivationConfig = EmbeddedDocumentField(ActivationConfig)
    #
    key_expression: str = StringField(default=None)
    alarm_config: "AlarmConfig" = EmbeddedDocumentField(AlarmConfig)

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["MetricAction"]:
        return MetricAction.objects.filter(id=oid).first()

    def clean(self):
        if not self.compose_inputs or not self.compose_inputs[0].metric_type:
            raise ValidationError({"compose_inputs": "Empty MetricType"})
        if not self.compose_expression:
            return

        # Same scope check
        scope = self.compose_inputs[0].metric_type.scope.table_name
        for ci in self.compose_inputs:
            if ci.metric_type.scope.table_name != scope:
                raise ValidationError(
                    {"compose_inputs": f"Metric {ci.metric_type.name} not in the scope {scope}"}
                )

        # Executable check
        try:
            get_fn(self.compose_expression)
        except SyntaxError as e:
            raise ValidationError({"compose_expression": f"Syntax error {e}"})
        except Exception as e:
            raise ValidationError({"compose_expression": f"{e}"})

        try:
            metric_fields = get_vars(self.compose_expression)
        except Exception as e:
            raise ValidationError({"compose_expression": str(e)})
        inputs = [mi.metric_type for mi in self.compose_inputs]
        for m_f in metric_fields:
            mt = MetricType.get_by_field_name(m_f, scope)
            if not mt or mt not in inputs:
                raise ValidationError(
                    {"compose_expression": f"Unknown variable {m_f} on expression"}
                )

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
        if self.compose_expression:
            r["compose_expression"] = self.compose_expression
        if self.activation_config and (
            self.activation_config.window_function or self.activation_config.activation_function
        ):
            r["activation_config"] = self.activation_config.json_data
        if self.deactivation_config and (
            self.deactivation_config.window_function or self.deactivation_config.activation_function
        ):
            r["deactivation_config"] = self.deactivation_config.json_data
        if self.key_expression:
            r["key_expression"] = self.key_expression
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

    def get_config(
        self,
        prefix: str = None,
        enable_dump: bool = False,
        rule_id: Optional[str] = None,
        thresholds: Optional[Any] = None,
        **kwargs,
    ) -> Optional[GraphConfig]:
        """
        Getting Graph config from MetricAction
        :param prefix: NodeID prefix
        :param enable_dump: Include DumpNode to config
        :param rule_id: Set if apply action to rule
        :param thresholds: Thresholds params
        :return:
        """
        # Configs
        node_configs = defaultdict(dict)
        for p in self.params:
            value = kwargs.get(p.name, p.default)
            if not value:
                continue
            node, config_name = p.name.split(".")
            try:
                value = p.clean_value(value)
            except ValueError:
                # Bad value for param
                continue
            node_configs[node][config_name] = value
        # Inputs Probe node
        inputs: List[InputItem] = []  # External Probe Inputs
        nodes: Dict[str, NodeItem] = {}
        prefix: str = f"{prefix}-" if prefix else ""
        for num, ci in enumerate(self.compose_inputs):
            inputs += [InputItem(name=ci.metric_type.field_name, node=ci.metric_type.field_name)]
        # Probe nodes
        if self.compose_expression:
            ci = []
            for ii in inputs:
                ci.append(InputItem(name=ii.name, node=ii.node, dynamic=True))
            nodes["compose"] = NodeItem(
                name=f"{prefix}compose",
                type="composeprobe",
                description="",
                config={"expression": self.compose_expression, "unit": "1"},
                inputs=ci,
            )
            g_input = InputItem(name="x", node=f"{prefix}compose")
        else:
            # If function is not set - only first input used
            g_input = InputItem(name="x", node=inputs[0].node)
        key_input = None
        # Activation
        if self.activation_config and self.activation_config.window_function:
            config = {
                "min_window": self.activation_config.min_window,
                "max_window": self.activation_config.max_window,
                "type": self.activation_config.window_type[0],
            }
            config.update(self.activation_config.window_config)
            nodes["activation-window"] = NodeItem(
                name=f"{prefix}activation-window",
                type=self.activation_config.window_function,
                config=config,
                inputs=[InputItem(name="x", node=g_input.node)],
            )
            key_input = InputItem(name="x", node=f"{prefix}activation-window")
        if self.activation_config and self.activation_config.activation_function:
            nodes["activation-function"] = NodeItem(
                name=f"{prefix}activation-function",
                type=self.activation_config.activation_function,
                config=self.activation_config.activation_config,
                inputs=[key_input or g_input],
            )
            key_input = InputItem(name="x", node=f"{prefix}activation-function")
        dkey_input = None
        # Deactivation
        if self.deactivation_config and self.deactivation_config.window_function:
            config = {
                "min_window": self.deactivation_config.min_window,
                "max_window": self.deactivation_config.max_window,
                "type": self.deactivation_config.window_type[0],
            }
            config.update(self.deactivation_config.window_config)
            nodes["deactivation-window"] = NodeItem(
                name=f"{prefix}deactivation-window",
                type=self.deactivation_config.window_function,
                config=config,
                inputs=[InputItem(name="x", node=g_input.node)],
            )
            dkey_input = InputItem(name="deactivate_x", node=f"{prefix}deactivation-window")
        if self.deactivation_config and self.deactivation_config.activation_function:
            nodes["deactivation-function"] = NodeItem(
                name=f"{prefix}deactivation-function",
                type=self.deactivation_config.activation_function,
                config=self.deactivation_config.activation_config,
                inputs=(
                    [g_input]
                    if not dkey_input
                    else [InputItem(name="x", node=f"{prefix}deactivation-window")]
                ),
            )
            dkey_input = InputItem(name="deactivate_x", node=f"{prefix}deactivation-function")
        # Key function
        if self.key_expression:
            kc_inputs = get_vars(self.key_expression)
            ci = []
            for ii in inputs:
                if ii.name not in kc_inputs:
                    continue
                ci.append(InputItem(name=ii.name, node=ii.node, dynamic=True))
            if ci:
                nodes["keycompose"] = NodeItem(
                    name=f"{prefix}keycompose",
                    type="composeprobe",
                    description="",
                    config={"expression": self.key_expression, "unit": "1"},
                    inputs=ci,
                )
                nodes["key"] = NodeItem(
                    name=f"{prefix}key",
                    type="key",
                    inputs=[
                        InputItem(name="key", node=f"{prefix}keycompose"),
                        key_input or g_input,
                    ],
                )
                key_input = InputItem(name="x", node=f"{prefix}key")
        if self.compose_metric_type:
            nodes["compose_{self.compose_metric_type.field_name}"] = NodeItem(
                name=f"{prefix}compose_{self.compose_metric_type.field_name}",
                type="probe",
                config={"units": "1"},
                inputs=[key_input or g_input],
            )
        # Alarm
        if self.alarm_config and self.alarm_config.alarm_class:
            nodes["alarm"] = NodeItem(
                name=f"{prefix}alarm",
                type="threshold" if thresholds else "alarm",
                inputs=[key_input or g_input],
                config={
                    "alarm_class": self.alarm_config.alarm_class.name,
                    "reference": self.alarm_config.reference
                    or "th:{{vars.rule}}:{{vars.action}}:{{object}}:{{alarm_class}}:{{';'.join(labels)}}",
                    "error_text_template": self.alarm_config.error_text_template,
                    "vars": [
                        VarItem(name="rule", value=str(rule_id)),
                        VarItem(name="action", value=str(self.id)),
                        VarItem(name="metric", value=str(self.compose_inputs[0].metric_type.name)),
                    ],
                },
            )
            if thresholds:
                nodes["alarm"].config["thresholds"] = thresholds
            if dkey_input:
                nodes["alarm"].inputs += [
                    InputItem(name=dkey_input.name, node=dkey_input.node, dynamic=True)
                ]
        # Apply param to Node config
        for node_id in node_configs:
            if node_id in nodes:
                nodes[node_id].config.update(node_configs[node_id])
        if enable_dump:
            nodes["dump"] = NodeItem(
                name=f"{prefix}dump",
                type="dump",
                inputs=inputs[:] + [key_input or g_input],
            )
            if dkey_input:
                nodes["dump"].inputs += [dkey_input]
        if not nodes:
            return
        return GraphConfig(nodes=list(nodes.values()))

    def iter_changed_datastream(self, changed_fields=None):
        from noc.pm.models.metricrule import MetricRule

        if config.datastream.enable_cfgmetricrules:
            for rid in MetricRule.objects.filter(actions__metric_action=self.id):
                yield "cfgmetricrules", rid.id
