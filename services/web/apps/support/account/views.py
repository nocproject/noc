# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# support.account application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.support.cp import CPClient
from noc.sa.interfaces.base import StringParameter, REStringParameter
from noc.core.translation import ugettext as _


class AccountApplication(ExtApplication):
    """
    support.account application
    """

    title = _("Account")
    menu = [_("Setup"), _("Account")]

    @view(url=r"^$", method=["GET"], access="launch", api=True)
    def api_get(self, request):
        c = CPClient()
        data = {}
        if c.has_account():
            data["account"] = c.account_info()
            for i in data["account"].get("industries", []):
                data["account"]["ind_%s" % i] = True
        if c.has_system():
            data["system"] = c.system_info()
        return data

    @view(
        url="^account/attach/$",
        method=["POST"],
        access="launch",
        api=True,
        validate={"name": StringParameter(), "password": StringParameter(required=False)},
    )
    def api_attach_account(self, request, name, password):
        c = CPClient()
        if c.has_account():
            self.response_forbidden()
        try:
            c.attach_account(name, password)
        except CPClient.Error as e:
            return {"status": False, "message": str(e)}
        return {"status": True, "message": "Ok"}

    @view(
        url="^account/$",
        method=["POST"],
        access="launch",
        api=True,
        validate={
            "name": REStringParameter(r"^[a-zA-Z0-9\.\-_]+$"),
            "email": StringParameter(),
            "org": StringParameter(),
            "country": REStringParameter(r"^[A-Z]{2}$"),
            "language": REStringParameter(r"^[A-Z]{2}$"),
            "password": StringParameter(required=False),
        },
    )
    def api_save_account(
        self,
        request,
        name,
        email,
        password=None,
        org=None,
        country=None,
        language=None,
        *args,
        **kwargs
    ):
        industries = [k[4:] for k in kwargs if k.startswith("ind_") and kwargs[k]]
        c = CPClient()
        if c.has_account():
            try:
                c.update_account(
                    name, email, country=country, language=language, org=org, industries=industries
                )
            except CPClient.Error as e:
                return {"status": False, "message": str(e)}
        else:
            # Create account
            try:
                c.create_account(
                    name,
                    email,
                    password,
                    org=org,
                    country=country,
                    language=language,
                    industries=industries,
                )
            except CPClient.Error as e:
                return {"status": False, "message": str(e)}
        return {"status": True, "message": "Account saved"}

    @view(
        url=r"^account/change_password/$",
        method=["POST"],
        access="launch",
        api=True,
        validate={"old_password": StringParameter(), "new_password": StringParameter()},
    )
    def api_change_password(self, request, old_password, new_password, *args, **kwargs):
        c = CPClient()
        if not c.has_account():
            return {"status": False, "message": "Account is not registred"}
        if old_password != c.account_password:
            return {"status": False, "message": "Invalid password"}
        c.change_password(new_password)
        return {"status": True, "message": "Password has been changed"}

    @view(
        url=r"^system/$",
        method=["POST"],
        access="launch",
        api=True,
        validate={
            "name": REStringParameter(r"^[a-zA-Z0-9\.\-_]+$"),
            "type": StringParameter(required=False),
            "description": StringParameter(required=False),
        },
    )
    def api_save_system(self, request, name, type=None, description=None, *args, **kwargs):
        c = CPClient()
        if c.has_system():
            try:
                c.update_system(name, type, description=description)
            except CPClient.Error as e:
                return {"status": False, "message": str(e)}
        else:
            # Create account
            try:
                c.create_system(name, type, description=description)
            except CPClient.Error as e:
                return {"status": False, "message": str(e)}
        return {"status": True, "message": "System saved"}
