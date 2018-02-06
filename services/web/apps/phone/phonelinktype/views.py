# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# phone.phonelinktype application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.phone.models.phonelinktype import PhoneLinkType
from noc.core.translation import ugettext as _


class PhoneLinkTypeApplication(ExtDocApplication):
    """
    PhoneLinkType application
    """
    title = "Phone Link Type"
    menu = [_("Setup"), _("Phone Link Types")]
    model = PhoneLinkType
