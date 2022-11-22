# ----------------------------------------------------------------------
# dev.spec application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.dev.models.spec import Spec
from noc.core.translation import ugettext as _


class SpecApplication(ExtDocApplication):
    """
    Spec application
    """

    title = "Spec"
    menu = [_("Setup"), _("Specs")]
    model = Spec
