# ---------------------------------------------------------------------
# vc.vlanfilter application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.vc.models.vlanfilter import VLANFilter
from noc.sa.interfaces.base import IntParameter
from noc.core.translation import ugettext as _


class VLANFilterApplication(ExtDocApplication):
    """
    VLANFilter application
    """

    title = _("VLAN Filter")
    menu = [_("Setup"), _("VLAN Filters")]
    model = VLANFilter
