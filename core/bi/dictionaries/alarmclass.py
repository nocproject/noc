# ----------------------------------------------------------------------
# Alarm Class dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import DictionaryModel
from noc.core.clickhouse.fields import StringField
from noc.fm.models.alarmclass import AlarmClass as AlarmClassModel


class AlarmClass(DictionaryModel):
    class Meta(object):
        name = "alarmclass"
        layout = "hashed"
        source_model = "fm.AlarmClass"
        incremental_update = True

    id = StringField()
    name = StringField()

    @classmethod
    def extract(cls, item: "AlarmClassModel"):
        return {
            "id": str(item.id),
            "name": item.name,
        }
