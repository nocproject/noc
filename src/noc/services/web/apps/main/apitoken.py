# ---------------------------------------------------------------------
# main.apitoken application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.http import HttpRequest

# NOC modules
from noc.services.web.base.extapplication import ExtApplication, api
from noc.services.web.base.access import PermitLogged
from noc.main.models.apitoken import APIToken
from noc.sa.interfaces.base import StringParameter


class APITokenApplication(ExtApplication):
    """
    APIToken Application
    """

    @api.get("^(?P<type>[^/]+)/$", access=PermitLogged())
    def api_get_token(self, request: HttpRequest, type):
        token = APIToken.objects.filter(type=type, user=request.user.id).first()
        if token:
            return {"type": token.type, "token": token.token}
        self.response_not_found()

    @api.post("^(?P<type>[^/]+)/$", access=PermitLogged(), validate={"token": StringParameter()})
    def api_set_token(self, request: HttpRequest, type, token=None):
        APIToken._get_collection().update_many(
            {"type": type, "user": request.user.id}, {"$set": {"token": token}}, upsert=True
        )
