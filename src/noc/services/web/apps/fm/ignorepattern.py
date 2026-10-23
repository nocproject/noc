# ---------------------------------------------------------------------
# fm.ignorepattern application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.http import HttpRequest

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, api
from noc.fm.models.ignorepattern import IgnorePattern
from noc.core.fm.event import EventSource
from noc.core.translation import ugettext as _


class IgnorePatternApplication(ExtDocApplication):
    """
    IgnorePattern application
    """

    title = _("Ignore Patterns")
    menu = [_("Setup"), _("Ignore Patterns")]
    model = IgnorePattern

    @api.post("^from_event/(?P<event_id>[0-9a-f]{24})/$", access="create")
    def api_from_event(self, request: HttpRequest, event_id):
        """
        Create ignore pattern rule from event
        :return:
        """
        req = self.parse_request_query(request)
        source = EventSource(req["source"])
        data = {"is_active": True}
        if source == EventSource.SYSLOG:
            data["description"] = req["message"]
            data["source"] = source.value
            data["pattern"] = req["message"]
        elif source == EventSource.SNMP_TRAP and "snmp_trap_oid" in req:
            data["description"] = req["snmp_trap_oid"]
            data["source"] = source.value
            data["pattern"] = req["snmp_trap_oid"]
        return data
