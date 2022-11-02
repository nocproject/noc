# ----------------------------------------------------------------------
# vc.vlantemplate application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.app.extdocapplication import ExtDocApplication
from noc.vc.models.vlantemplate import VLANTemplate
from noc.core.translation import ugettext as _


class VLANTemplateApplication(ExtDocApplication):
    """
    VLANTemplate application
    """

    title = "VLAN Template"
    menu = [_("Setup"), _("VLAN Templates")]
    model = VLANTemplate
