# ---------------------------------------------------------------------
# sa.discoveredobject application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from bson import ObjectId

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.services.web.base.decorators.state import state_handler
from noc.sa.models.discoveredobject import DiscoveredObject, CheckStatus
from noc.sa.interfaces.base import (
    ListOfParameter,
    StringListParameter,
    DictListParameter,
    StringParameter,
    BooleanParameter,
    IntParameter,
)
from noc.wf.models.workflow import Workflow
from noc.wf.models.state import State
from noc.core.translation import ugettext as _


@state_handler
class DiscoveredObjectApplication(ExtDocApplication):
    """
    Discovered Object
    """

    title = _("Discovered Object")
    menu = _("Discovered Object")
    icon = "icon_monitor"
    model = DiscoveredObject
    default_ordering = ["address"]
    query_fields = ["address", "description", "hostname"]  # Use all unique fields by default
    query_condition = "contains"

    def instance_to_dict_list(self, o, fields=None, nocustom=False):
        if isinstance(o, CheckStatus):
            if not o.port:
                return o.name
            return f"{o.name}:{o.port}"
        return super().instance_to_dict_list(o, fields, nocustom)

    def instance_to_dict(self, o, fields=None, nocustom=False):
        r = super().instance_to_dict(o, fields, nocustom)
        if "checks" in r:
            r["checks"] = [
                {"name": c.name, "port": c.port, "status": c.status, "label": c.name}
                for c in o.checks
            ]
        if "managed_object" in r:
            r["synced"] = {"id": "", "model": "sa.ManagedObject"}
        # if isinstance(o, CheckStatus):
        #    if not o.port:
        #        return o.name
        #    return f"{o.name}:{o.port}"
        return r

    def cleaned_query(self, q):
        if "addresses" in q:
            if isinstance(q["addresses"], list):
                q["address__in"] = q["addresses"]
            else:
                q["address__in"] = [q["addresses"]]
            del q["addresses"]
        if "checks" in q:
            checks = q.pop("checks")
            if not isinstance(checks, list):
                checks = [checks]
            for c in checks:
                c_name, *port, status = c.split("__")
                if not port:
                    q["checks__match"] = {"name": c_name, "status": status == "true"}
                else:
                    q["checks__match"] = {
                        "name": c_name,
                        "port": int(port[0]),
                        "status": status == "true",
                    }
            # SNMPv2c__true
        if "source" in q:
            source = q.pop("source")
            if not isinstance(source, list):
                source = [source]
            q["sources__in"] = [{"scan": "network-scan"}.get(s, s) for s in source]
        if "last_update" in q:
            del q["last_update"]
        r = super().cleaned_query(q)
        return r

    @view(url=r"actions/sync_records/$", method=["POST"], access="action", api=True)
    def api_sync_action(self, request):
        print(request)
        return {"status": True}

    @view(url=r"actions/send_event/$", method=["POST"], access="action", api=True)
    def api_send_event_action(self, request):

        print(request)
        return {"status": True}

    @view(url=r"^template_lookup/$", method=["GET"], access="read", api=True)
    def api_sync_template_lookup(self, request):
        x = str(ObjectId())
        r = [
            {
                "id": x,
                "label": _("Default Managed Object"),
                "is_default": True,
                "args": {"action": "sync_records", "template": x},
            }
        ]
        return r

    @view(url=r"^action_lookup/$", method=["GET"], access="read", api=True)
    def api_action_lookup(self, request):
        r = {"approve": {
                "id": f"active_event",
                "label": "Approve",
                "is_default": True,
                "args": {"action": "send_event", "event": "approve"},
            }
        }
        wfs = Workflow.objects.filter(allowed_models__in=["sa.DiscoveredObject"])
        for st in State.objects.filter(workflow__in=wfs):
            if not st.event or st.event in r:
                continue
            r[st.event] = {
                    "id": f"active_event",
                    "label": str(st),
                    "is_default": False,
                    "args": {"action": "send_event", "event": st.event},
                }
        return list(r.values())

    @view(
        url=r"^scan_run/$",
        method=["POST"],
        access="scan",
        api=True,
        validate={
            "addresses": StringListParameter(),
            # "checks": DictListParameter(
            #     attrs={
            #         "name": StringParameter(required=True),
            #         "port": IntParameter(required=False, default=0),
            #     }, required=False,
            # ),
            "checks": ListOfParameter(StringParameter(), required=False),
            "credentials": StringListParameter(required=False),
        },
    )
    def api_sync_lookup(self, request, addresses, checks=None, credentials=None):
        return {"status": True}
