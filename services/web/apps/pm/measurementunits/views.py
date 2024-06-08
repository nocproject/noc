# ----------------------------------------------------------------------
# pm.measurementunits application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.interfaces.base import ColorParameter
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.pm.models.measurementunits import MeasurementUnits
from noc.core.translation import ugettext as _


class MeasurementUnitsApplication(ExtDocApplication):
    """
    MeasurementUnits application
    """

    title = "MeasurementUnits"
    menu = [_("Setup"), _("Measurement Units")]
    model = MeasurementUnits

    clean_fields = {"dashboard_sr_color": ColorParameter()}
