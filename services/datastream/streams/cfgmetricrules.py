# ----------------------------------------------------------------------
# cfgmetricrules
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Dict

# NOC modules
from noc.core.datastream.base import DataStream
from noc.pm.models.metricrule import MetricRule


class CfgMetricRuleDataStream(DataStream):
    name = "cfgmetricrules"

    @classmethod
    def get_object(cls, id: str) -> Dict[str, Any]:
        rule: "MetricRule" = MetricRule.objects.filter(id=id).first()
        if not rule or not rule.is_active or not rule.actions:
            raise KeyError()
        return MetricRule.get_config(rule)
