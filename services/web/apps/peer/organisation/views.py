# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# peer.organisation application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication
from noc.peer.models import Organisation


class OrganisationApplication(ExtModelApplication):
    """
    Person application
    """
    title = _("Organisations")
    menu = [_("Setup"), _("Organisations")]
    model = Organisation
    query_fields = ["organisation__icontains", "org_name__icontains"]
