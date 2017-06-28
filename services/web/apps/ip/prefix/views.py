# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ip.prefix application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication, view
from noc.ip.models import Prefix


class PrefixApplication(ExtModelApplication):
    """
    Prefix application
    """
    title = "Prefix"
    model = Prefix
