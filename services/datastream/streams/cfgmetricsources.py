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
        if not source.has_configured_metrics:
            print("Not Configured metrics")
            raise KeyError("Not Configured metrics")
        config = source.get_metric_config(source)
        # Used bi_id as id
        config["id"] = str(sid)
        return config

    @classmethod
    def get_deleted_object(cls, sid):
        """
        Generate item for deleted object
        :param sid:
        :return:
        """
        source_type, sid = sid.split("::")
        return {"id": str(sid), "$deleted": True}
