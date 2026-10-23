# ---------------------------------------------------------------------
# inv.inv contacts plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.http import HttpRequest

# NOC modules
from noc.inv.models.object import Object
from noc.sa.interfaces.base import UnicodeParameter
from .base import InvPlugin


class ContactsPlugin(InvPlugin):
    name = "contacts"
    js = "NOC.inv.inv.plugins.contacts.ContactsPanel"

    def init_plugin(self):
        super().init_plugin()
        self.add_view(
            f"api_plugin_{self.name}_set_contacts",
            self.api_set_contacts,
            url=f"^(?P<id>[0-9a-f]{{24}})/plugin/{self.name}/$",
            method=["POST"],
            validate={
                "administrative": UnicodeParameter(),
                "billing": UnicodeParameter(),
                "technical": UnicodeParameter(),
            },
        )

    def get_data(self, request: HttpRequest, o):
        return {
            "id": str(o.id),
            "contacts_administrative": o.get_data("contacts", "administrative") or "",
            "contacts_billing": o.get_data("contacts", "billing") or "",
            "contacts_technical": o.get_data("contacts", "technical") or "",
        }

    def api_set_contacts(self, request: HttpRequest, id, administrative, billing, technical):
        o = self.app.get_object_or_404(Object, id=id)
        administrative = (administrative or "").strip()
        billing = (billing or "").strip()
        technical = (technical or "").strip()
        if administrative:
            o.set_data("contacts", "administrative", administrative)
        else:
            o.reset_data("contacts", "administrative")
        if billing:
            o.set_data("contacts", "billing", billing)
        else:
            o.reset_data("contacts", "billing")
        if technical:
            o.set_data("contacts", "technical", technical)
        else:
            o.reset_data("contacts", "technical")
        o.save()
        return True
