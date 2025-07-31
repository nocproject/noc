# ---------------------------------------------------------------------
# inv.inv alarm plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Dict, DefaultDict, List, Any
from collections import defaultdict

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.inv.models.object import Object
from noc.fm.models.activealarm import ActiveAlarm, PathCode
from noc.core.feature import Feature
from .base import InvPlugin


class AlarmPlugin(InvPlugin):
    name = "job"
    js = "NOC.inv.inv.plugins.alarm.AlarmPanel"
    required_feature = Feature.FGALARMS

    ROOT_ALARM_CLS = "fa fa-exclamation-triangle"
    ALARM_CLS = "fa fa-exclamation"

    def init_plugin(self):
        super().init_plugin()

    def get_data(self, request, obj: Object):
        def get_node(a: ObjectId) -> Dict[str, Any]:
            alarm = alarms[a]
            children_alarms = children[a]
            r: Dict[str, Any] = {
                "id": str(a),
                "title": alarm.subject,
                "alarm_class": alarm.alarm_class.name,
                "iconCls": self.ROOT_ALARM_CLS if children_alarms else self.ALARM_CLS,
            }
            if children_alarms:
                r["expanded"] = (True,)
                r["children"] = [get_node(c) for c in children_alarms]
            else:
                r["leaf"] = True
            return r

        # @todo: Show external root alarms
        # @todo: Relative path
        current = obj.as_resource()
        # Get all alarms
        alarms: Dict[ObjectId, ActiveAlarm] = {
            a.id: a
            for a in ActiveAlarm.objects.filter(
                resource_path__elemMatch={"code": PathCode.OBJECT.value, "path": current}
            )
        }
        # parent -> list of children
        children: DefaultDict[ObjectId, List[ObjectId]] = defaultdict(list)
        # top-level
        top: List[ObjectId] = []
        for a in alarms.values():
            if a.parent and a.parent.id in alarms:
                children[a.parent.id].append(a.id)
            else:
                top.append(a.id)
        r = [get_node(x) for x in top]
        return {"expanded": True, "children": r}
