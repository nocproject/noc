# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# peer.communitytype application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication
from noc.peer.models import CommunityType


class CommunityTypeApplication(ExtModelApplication):
    """
    Community Types application
    """
    title = _("Community Types")
    menu = [_("Setup"), _("Community Types")]
    model = CommunityType
    query_fields = ["name__icontains"]
