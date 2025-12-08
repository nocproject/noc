# ---------------------------------------------------------------------
# phone.phonenumberprofile application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.phone.models.phonenumberprofile import PhoneNumberProfile
from noc.core.translation import ugettext as _


class PhoneNumberProfileApplication(ExtDocApplication):
    """
    PhoneNumberProfile application
    """

    title = "Number Profile"
    menu = [_("Setup"), _("Number Profiles")]
    model = PhoneNumberProfile
