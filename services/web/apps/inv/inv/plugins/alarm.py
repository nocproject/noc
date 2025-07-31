# ---------------------------------------------------------------------
# inv.inv alarm plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Dict

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

    def init_plugin(self):
        super().init_plugin()

    def get_data(self, request, obj: Object):
        current = obj.as_resource()
        # Get all alarms
        alarms: Dict[ObjectId, ActiveAlarm] = {
            a.id: a
            for a in ActiveAlarm.objects.filter(
                resource_path__elemMatch={"code": PathCode.OBJECT.value, "path": current}
            )
        }
        print("@" * 72)
        print(">>>", alarms)
        return {}
