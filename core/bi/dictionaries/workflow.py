# ----------------------------------------------------------------------
# Workflow BI dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import DictionaryModel
from noc.core.clickhouse.fields import StringField, BooleanField
from noc.wf.models.workflow import Workflow as WorkflowModel


class Workflow(DictionaryModel):
    class Meta(object):
        name = "workflow"
        layout = "hashed"
        source_model = "wf.Workflow"
        incremental_update = True

    id = StringField()
    name = StringField()
    is_active = BooleanField()

    @classmethod
    def extract(cls, item: "WorkflowModel"):
        return {
            "id": str(item.id),
            "name": item.name,
            "is_active": int(item.is_active or 0),
        }
