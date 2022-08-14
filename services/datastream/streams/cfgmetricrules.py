# ----------------------------------------------------------------------
# cfgmetricrules
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
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
    def get_object(cls, oid: str) -> Dict[str, Any]:
        m_rule: "MetricRule" = MetricRule.objects.filter(id=oid).first()
        if not m_rule or not m_rule.is_active or not m_rule.actions:
            raise KeyError()
        r = {
            "id": str(m_rule.id),
            "name": m_rule.name,
            "actions": [],
            "match": [],
        }
        for action in m_rule.actions:
            if not action.is_active:
                continue
            r_action = {
                "id": str(action.metric_action.id),
                "name": str(action.metric_action),
                "graph_config": action.metric_action.get_config(
                    **action.metric_action_params
                ).dict(),
                "inputs": [],
            }
            for mt in action.metric_action.compose_inputs:
                r_action["inputs"] += [
                    {
                        "input_name": mt.input_name,
                        "probe_id": mt.metric_type.field_name,
                        "sender_id": mt.metric_type.scope.table_name,
                    }
                ]
            r["actions"] += [r_action]
        for match in m_rule.match or []:
            if not match.labels and not match.exclude_labels:
                continue
            r["match"] += [
                {
                    "labels": match.labels or [],
                    "exclude_labels": match.exclude_labels or [],
                }
            ]
        return r
