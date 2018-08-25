# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# peer.communitytype application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication
from noc.peer.models.communitytype import CommunityType
from noc.core.translation import ugettext as _


class CommunityTypeApplication(ExtModelApplication):
    """
    Community Types application
    """
    title = _("Community Types")
    menu = [_("Setup"), _("Community Types")]
    model = CommunityType
    query_fields = ["name__icontains"]
