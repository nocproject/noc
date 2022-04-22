# ----------------------------------------------------------------------
# Interface Description dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import DictionaryModel
from noc.core.clickhouse.fields import StringField, UInt64Field
from noc.inv.models.subinterface import SubInterface
from noc.core.text import ch_escape


class InterfaceDescription(DictionaryModel):
    class Meta(object):
        name = "interfacedescription"
        layout = "complex_key_hashed"
        source_model = "inv.SubInterface"
        primary_key = ("bi_id", "name")
        incremental_update = True

    name = StringField()
    description = StringField()
    service = UInt64Field()

    @classmethod
    def extract(cls, item: "SubInterface"):
        return {
            "bi_id": item.managed_object.bi_id,
            "name": item.name,
            "description": ch_escape(item.description or ""),
            "service": item.service.bi_id if item.service else 0,
        }
