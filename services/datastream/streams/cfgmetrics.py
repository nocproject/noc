# ----------------------------------------------------------------------
# cfgmetricscollector
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Dict

# NOC modules
from noc.core.datastream.base import DataStream
from noc.pm.models.metrictype import MetricType


class CfgMetricsCollectorDataStream(DataStream):
    name = "cfgmetrics"

    @classmethod
    def get_object(cls, id: str) -> Dict[str, Any]:
        mt = MetricType.get_by_id(id)
        cfg = MetricType.get_config(mt)
        if not mt:
            raise KeyError()
        return cfg
