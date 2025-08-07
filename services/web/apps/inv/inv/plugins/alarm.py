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
from noc.inv.models.channel import Channel
from noc.fm.models.alarmseverity import AlarmSeverity
from noc.fm.models.activealarm import ActiveAlarm, PathCode
from noc.core.feature import Feature
from .base import InvPlugin


class AlarmPlugin(InvPlugin):
    name = "alarm"
    js = "NOC.inv.inv.plugins.alarm.AlarmPanel"
    required_feature = Feature.FGALARMS

    ROOT_ALARM_CLS = "fa fa-exclamation-triangle"
    ALARM_CLS = "fa fa-exclamation"

    def init_plugin(self):
        super().init_plugin()

    def get_data(self, request, obj: Object):
        def get_path(resource: str) -> List[Dict[str, str]]:
            obj, name = Object.from_resource(resource)
            if not obj:
                return []
            path: List[Dict[str, str]] = []
            if name:
                path.append({"id": "", "title": name})
            while obj.parent and obj.as_resource() != current:
                if obj.parent_connection:
                    path.append({"id": "", "title": obj.parent_connection})
                else:
                    path.append({"id": str(obj.id), "title": obj.name or "-"})
                obj = obj.parent
            return list(reversed(path))

        def get_node(a: ObjectId) -> Dict[str, Any]:
            alarm = alarms[a]
            severity = AlarmSeverity.get_severity(alarm.severity)
            children_alarms = children[a]
            r: Dict[str, Any] = {
                "id": str(a),
                "title": alarm.subject,
                "alarm_class": str(alarm.alarm_class.id),
                "alarm_class__label": alarm.alarm_class.name,
                "channel": "",
                "channel__label": "",
                "object": "",
                "iconCls": self.ROOT_ALARM_CLS if children_alarms else self.ALARM_CLS,
                "row_class": severity.style.css_class_name,
                "severity": alarm.severity,
                "severity__label": severity.name,
                "timestamp": self.app.to_json(alarm.timestamp),
                "duration": alarm.duration,
            }
            ch_path = alarm.get_resource_path(PathCode.CHANNEL)
            if ch_path:
                ch = Channel.get_by_id(ch_path[0][2:])
                if ch:
                    r["channel"] = str(ch.id)
                    r["channel__label"] = ch.name
            obj_path = alarm.get_resource_path(PathCode.OBJECT)
            if obj_path:
                r["object"] = get_path(obj_path[-1])
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
            if a.root and a.root in alarms:
                children[a.root].append(a.id)
            else:
                top.append(a.id)
        r = [get_node(x) for x in top]
        return {"expanded": True, "children": r}
