# ----------------------------------------------------------------------
# vendor dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import DictionaryModel
from noc.core.clickhouse.fields import StringField
from noc.inv.models.vendor import Vendor as VendorModel


class Vendor(DictionaryModel):
    class Meta(object):
        name = "vendor"
        layout = "hashed"
        source_model = "inv.Vendor"
        incremental_update = True

    id = StringField()
    name = StringField()

    @classmethod
    def extract(cls, item: "VendorModel"):
        return {
            "id": str(item.id),
            "name": item.name,
        }
