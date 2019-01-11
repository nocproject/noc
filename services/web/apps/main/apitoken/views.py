# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# main.apitoken application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.lib.app.access import PermitLogged
from noc.main.models.apitoken import APIToken
from noc.sa.interfaces.base import StringParameter


class APITokenApplication(ExtApplication):
    """
    APIToken Application
    """
    @view("^(?P<type>[^/]+)/$", method=["GET"], access=PermitLogged(), api=True)
    def api_get_token(self, request, type):
        token = APIToken.objects.filter(type=type, user=request.user.id).first()
        if token:
            return {
                "type": token.type,
                "token": token.token
            }
        else:
            self.response_not_found()

    @view(
        "^(?P<type>[^/]+)/$", method=["POST"], access=PermitLogged(),
        validate={
            "token": StringParameter()
        }, api=True
    )
    def api_set_token(self, request, type, token=None):
        APIToken._get_collection().update({
            "type": type,
            "user": request.user.id
        }, {
            "$set": {
                "token": token
            }
        }, upsert=True)
