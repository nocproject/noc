# ---------------------------------------------------------------------
# MIMEType Manager
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.main.models.mimetype import MIMEType
from noc.services.web.base.extmodelapplication import ExtModelApplication


class MIMETypeApplication(ExtModelApplication):
    title = _("MIME Types")
    model = MIMEType
    menu = [_("Setup"), _("MIME Types")]
