# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.unknownmodel application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.inv.models.unknownmodel import UnknownModel
from noc.sa.interfaces.base import ListOfParameter, DocumentParameter
from noc.core.translation import ugettext as _


class UnknownModelApplication(ExtDocApplication):
    """
    UnknownModel application
    """
    title = "Unknown Models"
    menu = "Unknown Models"
    model = UnknownModel

    query_condition = "icontains"
    query_fields = ["vendor", "managed_object", "platform",
                    "part_no", "description"]

    @view(url="^actions/remove/$", method=["POST"],
          access="launch", api=True,
          validate={
              "ids": ListOfParameter(
                  element=DocumentParameter(UnknownModel),
                  convert=True
              )
          })
    def api_action_run_discovery(self, request, ids):
        UnknownModel.objects.filter(id__in=[x.id for x in ids])
        return _("Cleaned")
