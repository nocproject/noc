# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# phone.phonelinktype application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app import ExtDocApplication
from noc.phone.models.phonelinktype import PhoneLinkType


class PhoneLinkTypeApplication(ExtDocApplication):
    """
    PhoneLinkType application
    """
    title = "Phone Link Type"
    menu = [_("Setup"), _("Phone Link Types")]
    model = PhoneLinkType
