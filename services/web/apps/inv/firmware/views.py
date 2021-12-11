# ---------------------------------------------------------------------
# inv.firmware application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.inv.models.firmware import Firmware
from noc.core.translation import ugettext as _


class FirmwareApplication(ExtDocApplication):
    """
    Firmware application
    """

    title = _("Firmware")
    menu = [_("Setup"), _("Firmware")]
    model = Firmware
    query_fields = ["full_name__icontains"]
    default_ordering = ["full_name"]
