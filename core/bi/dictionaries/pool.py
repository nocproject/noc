# ----------------------------------------------------------------------
# pool dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import DictionaryModel
from noc.core.clickhouse.fields import StringField
from noc.main.models.pool import Pool as PoolModel


class Pool(DictionaryModel):
    class Meta(object):
        name = "pool"
        layout = "hashed"
        source_model = "main.Pool"
        incremental_update = True

    id = StringField()
    name = StringField()

    @classmethod
    def extract(cls, item: "PoolModel"):
        return {
            "id": str(item.id),
            "name": item.name,
        }
