# ---------------------------------------------------------------------
# phone.dialplan application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.phone.models.dialplan import DialPlan
from noc.services.web.base.extdocapplication import ExtDocApplication


class DialPlanApplication(ExtDocApplication):
    """
    DialPlan application
    """

    title = "DialPlan"
    menu = [_("Setup"), _("DialPlan")]
    model = DialPlan
