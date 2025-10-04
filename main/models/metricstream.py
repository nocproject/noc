# ----------------------------------------------------------------------
# MetricsStream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Dict, Any, Callable
from threading import Lock

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    ReferenceField,
    ListField,
    EmbeddedDocumentField,
)

# NOC Modules
from noc.core.mongo.fields import PlainReferenceField
from noc.pm.models.metricscope import MetricScope
from noc.pm.models.metrictype import MetricType

transform_code = {}
code_lock = Lock()


class StreamField(EmbeddedDocument):
    meta = {"strict": False}
    metric_type = ReferenceField(MetricType, required=True)
    external_alias = StringField(default=False)
    expose_mx = BooleanField(default=True)
    expose_condition = BooleanField(default=False)


class MetricStream(Document):
    meta = {
        "collection": "metricstream",
        "strict": False,
        "auto_create_index": False,
    }

    scope = PlainReferenceField(MetricScope, unique=True)
    is_active = BooleanField(default=True)
    # Metric scope reference
    fields = ListField(EmbeddedDocumentField(StreamField))

    def __str__(self):
        return f"{self.scope.name or ''}"
        # return self.scope

    def _get_transform_code(self) -> str:
        r = ["def q_mx(input):"]
        if not self.fields:
            # No path
            r += ["    return {}"]
            return "\n".join(r)
        r += [
            "    if not input:",
            "        return {}",
            "    v = {",
            f'    "scope": "{self.scope.name}",',
            '    "bi_id": input["managed_object"],',
            '    "labels": input.get("labels", []),',
            '    "meta": input.get("meta"),    }',
            '    if "ts" in input:',
            '        v["ts"] = input["ts"].replace(" ", "T")',
            '    if "service" in input:',
            '        v["service"] = input["service"]',
        ]
        if self.scope.enable_timedelta:
            r += [
                '    if "time_delta" in input:',
                '        v["time_delta"] = input["time_delta"]',
            ]
        for f in self.fields:
            if f.expose_condition:
                r += [f'    if not input.get("{f.metric_type.field_name}"):', "        return None"]
            if not f.expose_mx:
                continue
            r += [
                f'    v["{f.external_alias or f.metric_type.field_name}"] = input.get("{f.metric_type.field_name}")'
            ]
        r += ["    return v"]
        return "\n".join(r)

    def _get_transform(self) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        """
        Generate label -> path function for scope
        :return:
        """
        fn = transform_code.get(self.scope.name)
        if not fn:
            with code_lock:
                fn = transform_code.get(self.scope.name)
                if fn:
                    return fn
                # Compile
                code = self._get_transform_code()
                eval(compile(code, "<string>", "exec"))
                fn = locals()["q_mx"]
                transform_code[self.scope.name] = fn
        return fn

    def to_mx(self, m: Dict[str, Any]) -> Dict[str, Any]:
        return self._get_transform()(m)
