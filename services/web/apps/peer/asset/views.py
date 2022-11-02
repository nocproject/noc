# ---------------------------------------------------------------------
# ASSet Manager
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.app.extmodelapplication import ExtModelApplication
from noc.peer.models.asset import ASSet
from noc.services.web.app.repoinline import RepoInline
from noc.core.translation import ugettext as _


class ASSetApplication(ExtModelApplication):
    """
    ASSet application
    """

    title = _("AS Sets")
    menu = _("AS Sets")
    model = ASSet
    query_fields = ["name__icontains", "description__icontains", "members__icontains"]
    rpsl = RepoInline("rpsl")
