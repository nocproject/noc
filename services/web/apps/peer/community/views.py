# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# peer.community application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication
from noc.peer.models.community import Community
from noc.core.translation import ugettext as _


class CommunityApplication(ExtModelApplication):
    """
    Community application
    """
    title = _("Communities")
    menu = _("Communities")
    model = Community
    query_fields = ["community__icontains", "description__icontains"]
