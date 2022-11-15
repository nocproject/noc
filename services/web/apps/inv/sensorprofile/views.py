# ----------------------------------------------------------------------
# inv.sensorprofile application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.inv.models.sensorprofile import SensorProfile
from noc.core.translation import ugettext as _


class SensorProfileApplication(ExtDocApplication):
    """
    SensorProfile application
    """

    title = "SensorProfile"
    menu = [_("Setup"), _("Sensor Profiles")]
    model = SensorProfile

    def field_row_class(self, o):
        return o.style.css_class_name if o.style else ""
