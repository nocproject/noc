# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ip.address application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication, view
from noc.ip.models.address import Address


class AddressApplication(ExtModelApplication):
    """
    Address application
    """
    title = "Address"
    model = Address
