# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# peer.maintainer application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication, view
from noc.peer.models import Maintainer, Person
from noc.sa.interfaces.base import (ListOfParameter, ModelParameter,
                                    StringParameter)
from noc.core.translation import ugettext as _


class MaintainerApplication(ExtModelApplication):
    """
    Maintainers application
    """
    title = _("Maintainers")
    menu = [_("Setup"), _("Maintainers")]
    model = Maintainer

