# ----------------------------------------------------------------------
# cfgmetricstarget datastream
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Dict

# NOC modules
from noc.core.datastream.base import DataStream
from noc.sa.models.managedobject import ManagedObject
from noc.models import get_model


class CfgMetricsTargetDataStream(DataStream):
    name = "cfgmetricstarget"

    @classmethod
    def get_object(cls, sid: str) -> Dict[str, Any]:
        # Split source by model_id and bi_id
        model, sid = sid.split("::")
        sid = int(sid)
        model = get_model(model)
        if not model:
            raise KeyError(f"Unknown metric source: {model}")
        source = model.objects.filter(bi_id=sid).first()
        if not source:
            raise KeyError(f"Source {model} with id {sid} not found")
        if not source.has_configured_metrics:
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
        if "::" in sid:
            source_type, sid = sid.split("::")
        return {"id": str(sid), "$deleted": True}

    @classmethod
    def get_meta(cls, data):
        return {"sharding_key": data.get("sharding_key") or 0}

    @classmethod
    def filter_shard(cls, instance, n_instances):
        r = super().filter_shard(instance, n_instances)
        return {"meta.sharding_key": r["_id"]}

    @classmethod
    def is_moved(cls, meta, meta_filters) -> bool:
        return False

    @classmethod
    def on_change(cls, data):
        if cls.F_DELETED in data or data["type"] != "managed_object":
            return None
        mo = ManagedObject.get_by_bi_id(data["id"])
        if mo.effective_metric_discovery_interval != int(data.get("discovery_interval")):
            mo.effective_metric_discovery_interval = int(data.get("discovery_interval"))
            mo.save()
        return True
