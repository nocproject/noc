# ---------------------------------------------------------------------
# sa.serviceprofile application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.sa.models.serviceprofile import ServiceProfile
from noc.core.translation import ugettext as _


class ServiceProfileApplication(ExtDocApplication):
    """
    ServiceProfile application
    """

    title = _("Service Profile")
    menu = [_("Setup"), _("Service Profiles")]
    model = ServiceProfile

    def instance_to_dict(self, o, fields=None, nocustom=False):
        r = super().instance_to_dict(o, fields=fields, nocustom=nocustom)
        if "instance_policy_settings" in r and r["instance_policy_settings"]:
            r["instance_policy_settings"] = [r["instance_policy_settings"]]
        return r

    def clean(self, data):
        if data.get("instance_policy_settings"):
            data["instance_policy_settings"] = data["instance_policy_settings"][0]
        else:
            del data["instance_policy_settings"]
        return super().clean(data)
