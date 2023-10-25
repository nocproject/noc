# ---------------------------------------------------------------------
# inv.unknownmodel application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.inv.models.unknownmodel import UnknownModel
from noc.sa.interfaces.base import ListOfParameter, DocumentParameter
from noc.core.translation import ugettext as _


class UnknownModelApplication(ExtDocApplication):
    """
    UnknownModel application
    """

    title = _("Unknown Models")
    menu = _("Unknown Models")
    model = UnknownModel

    query_condition = "icontains"
    query_fields = ["vendor", "managed_object", "platform", "part_no", "description"]

    @view(
        url="^actions/remove/$",
        method=["POST"],
        access="launch",
        api=True,
        validate={"ids": ListOfParameter(element=DocumentParameter(UnknownModel), convert=True)},
    )
    def api_action_run_discovery(self, request, ids):
        objects = UnknownModel.objects.filter(id__in=[x.id for x in ids])
        self.logger.debug("Group action on '%s'", objects)
        for o in objects:
            self.logger.debug("Delete '%s'", o)
            o.delete()

        return _("Cleaned")
