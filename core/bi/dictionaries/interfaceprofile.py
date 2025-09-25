# ----------------------------------------------------------------------
# Interface Profile dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import DictionaryModel
from noc.core.clickhouse.fields import StringField, UInt8Field
from noc.inv.models.interfaceprofile import InterfaceProfile as InterfaceProfileModel


class InterfaceProfile(DictionaryModel):
    class Meta(object):
        name = "interfaceprofile"
        layout = "hashed"
        source_model = "inv.InterfaceProfile"
        incremental_update = True

    id = StringField()
    name = StringField()
    is_uni = UInt8Field()

    @classmethod
    def extract(cls, item: "InterfaceProfileModel"):
        return {
            "id": str(item.id),
            "name": item.name,
            "is_uni": int(item.is_uni or 0),
        }
