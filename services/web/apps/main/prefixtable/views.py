# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# main.prefixtable application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication, view
from noc.lib.app.modelinline import ModelInline
from noc.main.models.prefixtable import PrefixTable, PrefixTablePrefix
from noc.sa.interfaces.base import (IPParameter, ListOfParameter,
                                    ModelParameter)
from noc.core.translation import ugettext as _


class PrefixTableApplication(ExtModelApplication):
    """
    PrefixTable application
    """
    title = _("Prefix Table")
    menu = [_("Setup"), _("Prefix Tables")]
    model = PrefixTable

    prefixes = ModelInline(PrefixTablePrefix)

    @view(
        url="^actions/test/$", method=["POST"],
        access="update", api=True,
        validate={
            "ids": ListOfParameter(element=ModelParameter(PrefixTable)),
            "ip": IPParameter()
        }
    )
    def api_action_test(self, request, ids, ip):
        return {
            "ip": ip,
            "result": [{
                "id": pt.id,
                "name": pt.name,
                "result": ip in pt
            } for pt in ids]
        }
