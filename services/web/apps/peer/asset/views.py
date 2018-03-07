# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ASSet Manager
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication, view
from noc.peer.models.asset import ASSet
from noc.sa.interfaces.base import ListOfParameter, ModelParameter
from noc.core.translation import ugettext as _


class ASSetApplication(ExtModelApplication):
    """
    ASSet application
    """
    title = _("AS Sets")
    menu = _("AS Sets")
    model = ASSet
    query_fields = ["name__icontains", "description__icontains",
                    "members__icontains"]

    @view(
        url="^actions/rpsl/$", method=["POST"],
        access="read", api=True,
        validate={
            "ids": ListOfParameter(element=ModelParameter(ASSet))
        }
    )
    def api_action_rpsl(self, request, ids):
        return "</br></br>".join([o.rpsl.replace("\n", "</br>") for o in ids])

    api_action_rpsl.short_description = "RPSL for selected objects"
