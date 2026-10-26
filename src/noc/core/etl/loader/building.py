# ----------------------------------------------------------------------
# Building loader
# ----------------------------------------------------------------------
# Copyright (C) 2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.gis.models.building import Building
from noc.gis.models.division import Division

from ..models.building import Building as BuildingModel
from .base import BaseLoader


class BuildingLoader(BaseLoader):
    """
    Building loader
    """

    name = "building"
    model = Building
    data_model = BuildingModel

    fields = [
        "id",
        "adm_division",
        "postal_code",
        "start_date",
        "end_date",
    ]

    mapped_fields = {
        "adm_division": "admdiv",
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        division_dict = {}
        for r in Division.objects.all():
            division_dict[r.id] = r
        self.clean_map["adm_division"] = lambda x: [x.parent for x in division_dict[x]]
