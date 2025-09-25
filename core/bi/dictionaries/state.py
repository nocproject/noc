# ----------------------------------------------------------------------
# State BI dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import DictionaryModel
from noc.core.clickhouse.fields import StringField, BooleanField
from noc.wf.models.state import State as StateModel


class State(DictionaryModel):
    class Meta(object):
        name = "state"
        layout = "hashed"
        source_model = "wf.State"
        incremental_update = True

    id = StringField()
    name = StringField()
    workflow = StringField()
    is_default = BooleanField()
    is_productive = BooleanField()

    @classmethod
    def extract(cls, item: "StateModel"):
        return {
            "id": str(item.id),
            "name": item.name,
            "workflow": item.workflow.name,
            "is_default": int(item.is_default or 0),
            "is_productive": int(item.is_productive or 0),
        }
