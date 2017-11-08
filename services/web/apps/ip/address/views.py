# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ip.address application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.ip.models import Address
# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication


class AddressApplication(ExtModelApplication):
    """
    Address application
    """
    title = "Address"
    model = Address
