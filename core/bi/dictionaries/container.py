# ----------------------------------------------------------------------
# Container dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import DictionaryModel
from noc.core.clickhouse.fields import StringField, ReferenceField
from noc.inv.models.object import Object
from noc.core.text import ch_escape


class Container(DictionaryModel):
    class Meta(object):
        name = "container"
        layout = "hashed"
        source_model = "inv.Object"
        incremental_update = True

    id = StringField()
    name = StringField()
    parent = ReferenceField("self")
    address_text = StringField()

    @classmethod
    def extract(cls, item: "Object"):
        return {
            "id": str(item.id),
            "name": ch_escape(item.name or ""),
            "parent": item.container.bi_id if item.container else 0,
            "address_text": ch_escape(item.get_address_text() or ""),
        }
