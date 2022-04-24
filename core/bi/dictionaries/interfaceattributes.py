# ----------------------------------------------------------------------
# Interface Attributes dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import DictionaryModel
from noc.core.clickhouse.fields import StringField, UInt64Field, UInt8Field
from noc.inv.models.interface import Interface
from noc.core.text import ch_escape


class InterfaceAttributes(DictionaryModel):
    class Meta(object):
        name = "interfaceattributes"
        layout = "complex_key_hashed"
        source_model = "inv.Interface"
        primary_key = ("bi_id", "name")
        incremental_update = True

    name = StringField()
    description = StringField()
    profile = StringField()
    in_speed = UInt64Field()
    is_uni = UInt8Field()
    service = UInt64Field()

    @classmethod
    def extract(cls, item: "Interface"):
        return {
            "bi_id": item.managed_object.bi_id,
            "name": item.name,
            "description": ch_escape(item.description or ""),
            "profile": item.profile.name,
            # iface speed in kbit/s convert to bit/s,
            # some vendors set speed -1 for iface down
            "in_speed": abs(item.in_speed or 0) * 1000,
            "is_uni": item.profile.is_uni,
            "service": item.service.bi_id if item.service else 0,
        }
