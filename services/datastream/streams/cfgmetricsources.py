# ----------------------------------------------------------------------
# cfgmetricsources datastream
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Dict

# NOC modules
from noc.core.datastream.base import DataStream
from noc.models import get_model


class CfgMetricSourcesDataStream(DataStream):
    name = "cfgmetricsources"

    @classmethod
    def get_object(cls, sid: str) -> Dict[str, Any]:
        # Split source by model_id and bi_id
        source_type, sid = sid.split("::")
        sid = int(sid)
        model = get_model(source_type)
        if not model:
            raise KeyError(f"Unknown metric source: {source_type}")
        source = model.objects.get(bi_id=sid)
        if not source:
            raise KeyError(f"Source {source_type} with id {sid} not found")
        config = source.get_metric_config(source)
        if not config or (not config["metrics"] and not config["items"]):
            raise KeyError("Not Configured metrics")
        # Used bi_id as id
        config["id"] = sid
        return config
