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
        building_dict = {}
        street_dict = {}
        for r in Building.objects.all():
            building_dict[r.id] = r
        for rec in Street.objects.all():
            street_dict[rec.id] = rec
        self.clean_map["building"] = lambda x: [x.building for x in building_dict[x]]
        self.clean_map["street"] = lambda x: [x.street for x in street_dict[x]]
