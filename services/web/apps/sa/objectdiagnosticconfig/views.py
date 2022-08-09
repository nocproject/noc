# ----------------------------------------------------------------------
# sa.objectdiagnosticconfig application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.sa.models.objectdiagnosticconfig import ObjectDiagnosticConfig
from noc.core.translation import ugettext as _


class DiagnosticConfigApplication(ExtDocApplication):
    """
    DiagnosticConfig application
    """

    title = "ObjectDiagnosticConfig"
    menu = [_("Setup"), _("ObjectDiagnosticConfigs")]
    model = ObjectDiagnosticConfig
    query_fields = ["name__icontains", "description__icontains"]
    default_ordering = ["name"]
