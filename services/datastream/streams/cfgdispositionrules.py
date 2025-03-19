# ----------------------------------------------------------------------
# cfgdispositionrules
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Dict

# NOC modules
from noc.core.datastream.base import DataStream
from noc.fm.models.dispositionrule import DispositionRule


class CfgDispositionRulesDataStream(DataStream):
    name = "cfgdispositionrules"

    @classmethod
    def get_object(cls, oid: str) -> Dict[str, Any]:
        rule = DispositionRule.get_by_id(oid)
        if not rule:
            raise KeyError()
        r = DispositionRule.get_rule_config()
        r["id"] = str(rule.id)
        return r
