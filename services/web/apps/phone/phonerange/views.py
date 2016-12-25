# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## phone.phonerange application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.phone.models.phonerange import PhoneRange
from noc.core.translation import ugettext as _


class PhoneRangeApplication(ExtDocApplication):
    """
    PhoneRange application
    """
    title = "Phone Range"
    menu = [_("Phone Ranges")]
    model = PhoneRange
    parent_model = PhoneRange
    parent_field = "parent"

    def field_total_numbers(self, o):
    	return o.total_numbers

