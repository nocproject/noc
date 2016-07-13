# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## peer.person application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.peer.models import Person
from noc.lib.app.repoinline import RepoInline
from noc.core.translation import ugettext as _


class PersonApplication(ExtModelApplication):
    """
    Person application
    """
    title = _("Persons/Roles")
    menu = [_("Setup"), _("Persons")]
    model = Person
    query_fields = ["nic_hdl__icontains","person__icontains"]

    rpsl = RepoInline("rpsl")
