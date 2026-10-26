# ---------------------------------------------------------------------
# phone.numbercategory application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.phone.models.numbercategory import NumberCategory
from noc.services.web.base.extdocapplication import ExtDocApplication


class NumberCategoryApplication(ExtDocApplication):
    """
    NumberCategory application
    """

    title = "Number Category"
    menu = [_("Setup"), _("Number Categories")]
    model = NumberCategory
