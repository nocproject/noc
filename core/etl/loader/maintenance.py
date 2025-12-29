# ----------------------------------------------------------------------
# Maintenance loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Dict, Any

# NOC modules
from .base import BaseLoader
from ..models.maintenance import Maintenance
from noc.maintenance.models.maintenance import Maintenance as MaintenanceModel
from noc.maintenance.models.maintenancetype import MaintenanceType


class MaintenanceLoader(BaseLoader):
    """
    Maintenance loader
    """

    name = "maintenance"
    model = MaintenanceModel
    data_model = Maintenance
    model_mappings = {"type": MaintenanceType}

    post_save_fields = {"objects"}
    type_model_map = {
        "service": "sa.Service",
        "managed_object": "sa.ManagedObject",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clean_map["type"] = MaintenanceType.get_by_name

    def post_save(self, o: MaintenanceModel, fields: Dict[str, Any]):
        """Processed maintenance object"""
        r = []
        for oo in fields.get("objects", []):
            t = oo.pop("type")
            oo["model_id"] = self.type_model_map[t]
            r.append(oo)
        o.update_remote_objects(r)
