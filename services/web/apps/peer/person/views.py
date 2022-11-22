# ---------------------------------------------------------------------
# peer.person application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extmodelapplication import ExtModelApplication
from noc.peer.models.person import Person
from noc.services.web.base.repoinline import RepoInline
from noc.core.translation import ugettext as _


class PersonApplication(ExtModelApplication):
    """
    Person application
    """

    title = _("Persons/Roles")
    menu = [_("Setup"), _("Persons")]
    model = Person
    query_fields = ["nic_hdl__icontains", "person__icontains"]

    rpsl = RepoInline("rpsl")
