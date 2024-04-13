# ----------------------------------------------------------------------
# cfgmetricrules
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
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
        for num, action in enumerate(m_rule.actions):
            if not action.is_active:
                continue
            if action.metric_type and action.thresholds:
                r["actions"] += [
                    {
                        "id": str(action.metric_type.id),
                        "name": str(f"Threshold_{action.metric_type.name}"),
                        "graph_config": action.get_config(rule_id=m_rule.id).model_dump(),
                        "inputs": [
                            {
                                "input_name": "in",
                                "probe_id": action.metric_type.field_name,
                                "sender_id": action.metric_type.scope.table_name,
                            }
                        ],
                    }
                ]
                continue
            elif not action.metric_action:
                continue
            r_action = {
                "id": str(action.metric_action.id),
                "name": str(action.metric_action),
                "graph_config": action.metric_action.get_config(
                    **action.metric_action_params,
                    rule_id=m_rule.id,
                    thresholds=action.thresholds,
                ).model_dump(),
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
