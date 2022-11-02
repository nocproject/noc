# ---------------------------------------------------------------------
# fm.ignorepattern application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.app.extdocapplication import ExtDocApplication, view
from noc.fm.models.ignorepattern import IgnorePattern
from noc.fm.models.utils import get_event
from noc.core.translation import ugettext as _


class IgnorePatternApplication(ExtDocApplication):
    """
    IgnorePattern application
    """

    title = _("Ignore Patterns")
    menu = [_("Setup"), _("Ignore Patterns")]
    model = IgnorePattern

    @view(url="^from_event/(?P<event_id>[0-9a-f]{24})/$", method=["GET"], access="create", api=True)
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
        data = {"is_active": True}
        if event.source == "syslog":
            data["description"] = event.raw_vars["message"]
            data["source"] = "syslog"
            data["pattern"] = event.raw_vars["message"]
        elif event.source == "SNMP Trap" and "SNMPv2-MIB::snmpTrapOID.0" in event.resolved_vars:
            data["description"] = event.resolved_vars["SNMPv2-MIB::snmpTrapOID.0"]
            data["source"] = "SNMP Trap"
            data["pattern"] = event.raw_vars.get("1.3.6.1.6.3.1.1.4.1.0")
        return data
