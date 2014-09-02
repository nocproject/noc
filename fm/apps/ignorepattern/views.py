# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.ignorepattern application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.fm.models import IgnorePattern
from noc.fm.models import get_event


class IgnorePatternApplication(ExtDocApplication):
    """
    IgnorePattern application
    """
    title = "Ignore Patterns"
    menu = "Setup | Ignore Patterns"
    model = IgnorePattern

    @view(url="^from_event/(?P<event_id>[0-9a-f]{24})/$",
          method=["GET"], access="create", api=True)
    def api_from_event(self, request, event_id):
        """
        Create ignore pattern rule from event
        :param request:
        :param event_id:
        :return:
        """
        event = get_event(event_id)
        if not event:
            self.response_not_found()
        data = { "is_active": True }
        if event.raw_vars["source"] == "syslog":
            data["description"] = event.raw_vars["message"]
            data["source"] = "syslog"
        elif (event.raw_vars["source"] == "SNMP Trap" and
              "SNMPv2-MIB::snmpTrapOID.0" in event.resolved_vars):
            data["description"] = event.resolved_vars["SNMPv2-MIB::snmpTrapOID.0"]
            data["source"] = "SNMP Trap"
        data["pattern"] = event.raw_vars["message"]
        return data
