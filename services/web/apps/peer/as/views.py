# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AS Manager
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication
from noc.peer.models.asn import AS
from noc.lib.app.repoinline import RepoInline
from noc.core.translation import ugettext as _


class ASApplication(ExtModelApplication):
    """
    AS application
    """
    title = _("AS")
    menu = [_("ASes")]
    model = AS

    rpsl = RepoInline("rpsl")
