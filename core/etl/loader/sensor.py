# ----------------------------------------------------------------------
# Sensor loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.sensor import Sensor
from noc.inv.models.object import Object
from noc.inv.models.sensor import Sensor as SensorModel


class SensorLoader(BaseLoader):
    """
    Sensor loader
    """

    name = "sensor"
    model = SensorModel
    data_model = Sensor

    discard_deferred = True
    workflow_event_model = False

    def find_object(self, v):
        """
        Find object by remote system/remote id
        :param v:
        :return:
        """
        r = super().find_object(v)
        if not r:
            oo = Object.get_managed(v["managed_object"])
            find_query = {"local_id": v["local_id"], "object": oo}
            r = self.model.objects.filter(**find_query).first()
        return r
