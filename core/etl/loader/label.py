# ----------------------------------------------------------------------
# Labels loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from typing import Dict, Any

# NOC modules
from .base import BaseLoader
from ..models.label import Label
from noc.main.models.label import Label as LabelModel


class LabelLoader(BaseLoader):
    """
    Label loader
    """

    name = "label"
    model = LabelModel
    data_model = Label

    def clean(self, item: Label) -> Dict[str, Any]:
        """
        Cleanup row and return a dict of field name -> value
        """
        r = {
            "name": item.name,
            "description": item.description,
            "is_protected": item.is_protected,
            "allow_models": [],
        }
        for k, v in item.model_dump().items():
            if k in self.model.ENABLE_MODEL_ID_MAP and v:
                r["allow_models"].append(self.model.ENABLE_MODEL_ID_MAP[k])
        r["remote_system"] = self.system.remote_system
        r["remote_id"] = self.clean_str(item.id)
        # Fill mapping
        return r
