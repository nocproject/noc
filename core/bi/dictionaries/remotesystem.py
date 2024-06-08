# ----------------------------------------------------------------------
# Remote System dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import DictionaryModel
from noc.core.clickhouse.fields import StringField
from noc.main.models.remotesystem import RemoteSystem as RemoteSystemModel


class RemoteSystem(DictionaryModel):
    class Meta(object):
        name = "remotesystem"
        layout = "hashed"
        source_model = "main.RemoteSystem"
        incremental_update = True

    id = StringField()
    name = StringField()
    description = StringField()

    @classmethod
    def extract(cls, item: "RemoteSystemModel"):
        return {
            "id": str(item.id),
            "name": item.name,
            "description": item.description or "",
        }
