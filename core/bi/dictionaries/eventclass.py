# ----------------------------------------------------------------------
# Event Class dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import DictionaryModel
from noc.core.clickhouse.fields import StringField
from noc.fm.models.eventclass import EventClass as EventClassModel


class EventClass(DictionaryModel):
    class Meta(object):
        name = "eventclass"
        layout = "hashed"
        source_model = "fm.EventClass"
        incremental_update = True

    id = StringField()
    name = StringField()

    @classmethod
    def extract(cls, item: "EventClassModel"):
        return {
            "id": str(item.id),
            "name": item.name,
        }
