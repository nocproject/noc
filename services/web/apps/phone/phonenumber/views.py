# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## phone.phonenumber application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.phone.models.phonenumber import PhoneNumber
from noc.core.translation import ugettext as _


class PhoneNumberApplication(ExtDocApplication):
    """
    PhoneNumber application
    """
    title = "Phone Number"
    menu = [_("Phone Number")]
    model = PhoneNumber
