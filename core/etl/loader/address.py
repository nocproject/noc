# ----------------------------------------------------------------------
# Address loader
# ----------------------------------------------------------------------
# Copyright (C) 2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.address import Address as AddressModel
from noc.gis.models.address import Address
from noc.gis.models.building import Building
from noc.gis.models.street import Street


class AddressLoader(BaseLoader):
    """
    Address loader
    """

    name = "address"
    model = Address
    data_model = AddressModel

    fields = [
        "id",
        "building",
        "street",
        "num",
        "num_letter",
    ]

    mapped_fields = {
        "building": "building",
        "street": "street",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clean_map["building"] = lambda x: [
            x.building for x in Building.objects.get(remote_id=x)
        ]
        self.clean_map["street"] = lambda x: [x.street for x in Street.objects.get_by_id(id=x)]
