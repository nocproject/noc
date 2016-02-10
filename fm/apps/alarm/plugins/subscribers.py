# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Subscribers plugin
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import AlarmPlugin
from noc.lib.text import split_alnum
from noc.inv.models.interface import Interface


class SubscribersPlugin(AlarmPlugin):
    name = "subscribers"

    def get_data(self, alarm, config):
        # Get subscriber interfaces
        interfaces = []
        for i in Interface.objects.filter(
            managed_object=alarm.managed_object.id
        ):
            if i.profile.is_customer:
                interfaces += [i]
        if not interfaces:
            return {}  # No customers
        return {
            "plugins": [("NOC.fm.alarm.plugins.Subscribers", {})],
            "subscribers": [{
                "interface": i.name,
                "profile": i.profile.name,
                "description": i.description
            } for i in sorted(interfaces, key=split_alnum)]
        }