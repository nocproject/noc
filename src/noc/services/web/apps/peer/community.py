# ---------------------------------------------------------------------
# peer.community application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.peer.models.community import Community
from noc.services.web.base.extmodelapplication import ExtModelApplication


class CommunityApplication(ExtModelApplication):
    """
    Community application
    """

    title = _("Communities")
    menu = _("Communities")
    model = Community
    query_fields = ["community__icontains", "description__icontains"]
