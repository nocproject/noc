# ----------------------------------------------------------------------
# inv.sensor application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.lib.app.decorators.state import state_handler
from noc.inv.models.sensor import Sensor
from noc.core.translation import ugettext as _


@state_handler
class SensorApplication(ExtDocApplication):
    """
    ResourceGroup application
    """

    title = "Sensor"
    menu = [_("Setup"), _("Sensor")]
    model = Sensor
    query_fields = ["label"]
    query_condition = "icontains"
