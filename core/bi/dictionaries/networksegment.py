# ----------------------------------------------------------------------
# NetworkSegment dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import DictionaryModel
from noc.core.clickhouse.fields import StringField, ReferenceField
from noc.inv.models.networksegment import NetworkSegment as NetworkSegmentModel


class NetworkSegment(DictionaryModel):
    class Meta(object):
        name = "networksegment"
        layout = "hashed"
        source_model = "inv.NetworkSegment"
        incremental_update = True

    id = StringField()
    name = StringField()
    parent = ReferenceField("self")

    @classmethod
    def extract(cls, item: "NetworkSegmentModel"):
        return {
            "id": str(item.id),
            "name": item.name,
            "parent": item.parent.bi_id if item.parent else 0,
        }
