# ----------------------------------------------------------------------
# Sensor loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.sensor import Sensor
from noc.inv.models.sensor import Sensor as SensorModel
from noc.pm.models.measurementunits import MeasurementUnits


class SensorLoader(BaseLoader):
    """
    Sensor loader
    """

    name = "sensor"
    model = SensorModel
    data_model = Sensor

    discard_deferred = True
    workflow_event_model = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clean_map["units"] = lambda x: MeasurementUnits.get_by_name(x) if x else None
