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
from noc.fm.models.ignorepattern import IgnorePattern, DATASTREAM_RULE_PREFIX


class CfgEventRulesDataStream(DataStream):
    name = "cfgeventrules"

    @classmethod
    def get_object(cls, oid: str) -> Dict[str, Any]:
        rule_type, *oid = str(oid).split(":")
        if rule_type == DATASTREAM_RULE_PREFIX:
            # IgnorePattern
            rule = IgnorePattern.get_by_id(oid[0])
        elif oid:
            rule = EventClassificationRule.get_by_id(oid[0])
        else:
            rule = EventClassificationRule.get_by_id(rule_type)
        if not rule:
            raise KeyError()
        if rule_type == DATASTREAM_RULE_PREFIX:
            r = IgnorePattern.get_rule_config(rule)
        else:
            r = EventClassificationRule.get_rule_config(rule)
        return r
