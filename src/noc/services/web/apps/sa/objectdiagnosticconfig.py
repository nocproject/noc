# ----------------------------------------------------------------------
# sa.objectdiagnosticconfig application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.sa.models.objectdiagnosticconfig import ObjectDiagnosticConfig
from noc.core.translation import ugettext as _


class DiagnosticConfigApplication(ExtDocApplication):
    """
    DiagnosticConfig application
    """

    title = "Object Diagnostic Config"
    menu = [_("Setup"), _("Object Diagnostic Configs")]
    model = ObjectDiagnosticConfig
    query_fields = ["name__icontains", "description__icontains"]
    default_ordering = ["name"]

    def instance_to_dict(self, o, fields=None, nocustom=False):
        r = super().instance_to_dict(o, fields=fields, nocustom=nocustom)
        for c in r.get("checks", []):
            c["check__label"] = c["check"]
        return r
