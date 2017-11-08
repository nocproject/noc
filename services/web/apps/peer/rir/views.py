# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# peer.rir application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication
from noc.peer.models import RIR


class RIRApplication(ExtModelApplication):
    """
    RIR application
    """
    title = _("RIR")
    menu = [_("Setup"), _("RIRs")]
    model = RIR
