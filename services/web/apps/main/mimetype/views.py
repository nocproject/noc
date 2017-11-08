# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MIMEType Manager
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication
from noc.main.models.mimetype import MIMEType


class MIMETypeApplication(ExtModelApplication):
    title = _("MIME Types")
    model = MIMEType
    menu = [_("Setup"), _("MIME Types")]
