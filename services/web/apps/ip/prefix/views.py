# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ip.prefix application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.ip.models import Prefix
# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication


class PrefixApplication(ExtModelApplication):
    """
    Prefix application
    """
    title = "Prefix"
    model = Prefix
