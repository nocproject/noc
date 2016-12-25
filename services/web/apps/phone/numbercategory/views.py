# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## phone.numbercategory application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.phone.models.numbercategory import NumberCategory
from noc.core.translation import ugettext as _


class NumberCategoryApplication(ExtDocApplication):
    """
    NumberCategory application
    """
    title = "Number Category"
    menu = [_("Setup"), _("Number Categories")]
    model = NumberCategory
