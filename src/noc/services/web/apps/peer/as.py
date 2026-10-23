# ---------------------------------------------------------------------
# AS Manager
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extmodelapplication import ExtModelApplication
from noc.peer.models.asn import AS
from noc.services.web.base.repoinline import RepoInline
from noc.core.translation import ugettext as _


class ASApplication(ExtModelApplication):
    """
    AS application
    """

    title = _("AS")
    menu = [_("ASes")]
    model = AS

    rpsl = RepoInline("rpsl")

    query_fields = ["as_name", "description"]
    int_query_fields = ["asn"]

    query_condition = "contains"
