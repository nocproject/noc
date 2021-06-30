# ----------------------------------------------------------------------
# Street loader
# ----------------------------------------------------------------------
# Copyright (C) 2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.street import Street as StreetModel
from noc.gis.models.street import Street
from noc.gis.models.division import Division


class StreetLoader(BaseLoader):
    """
    Street loader
    """

    name = "street"
    model = Street
    data_model = StreetModel

    fields = [
        "id",
        "parent",
        "name",
        "short_name",
        "start_date",
        "end_date",
    ]

    mapped_fields = {
        "parent": "admdiv",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clean_map["parent"] = lambda x: [x.parent for x in Division.objects.get_by_id(id=x)]
