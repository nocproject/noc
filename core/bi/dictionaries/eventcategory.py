# ----------------------------------------------------------------------
# Event Category dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import DictionaryModel
from noc.core.clickhouse.fields import StringField, ReferenceField
from noc.fm.models.eventcategory import EventCategory as EventCategoryModel


class EventCategory(DictionaryModel):
    class Meta(object):
        name = "eventcategory"
        layout = "hashed"
        source_model = "fm.EventCategory"
        incremental_update = True

    id = StringField()
    name = StringField()
    parent = ReferenceField("self")

    @classmethod
    def extract(cls, item: "EventCategoryModel"):
        return {
            "id": str(item.id),
            "name": item.name,
            "parent": item.parent.bi_id if item.parent else 0,
        }
