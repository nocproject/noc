# ----------------------------------------------------------------------
# cfgeventrules
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Dict

# NOC modules
from noc.core.datastream.base import DataStream
from noc.fm.models.eventclassificationrule import EventClassificationRule


class CfgEventRulesDataStream(DataStream):
    name = "cfgeventrules"

    @classmethod
    def get_object(cls, oid: str) -> Dict[str, Any]:
        rule = EventClassificationRule.get_by_id(oid)
        if not rule:
            raise KeyError()
        r = EventClassificationRule.get_rule_config(rule)
        r["id"] = str(rule.id)
        return r
