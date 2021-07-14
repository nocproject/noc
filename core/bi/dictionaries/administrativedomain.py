# ----------------------------------------------------------------------
# AdministrativeDomain dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import DictionaryModel
from noc.core.clickhouse.fields import StringField, ReferenceField, UInt64Field
from noc.sa.models.administrativedomain import AdministrativeDomain as AdministrativeDomainModel


class AdministrativeDomain(DictionaryModel):
    class Meta(object):
        name = "administrativedomain"
        layout = "hashed"
        source_model = "sa.AdministrativeDomain"
        incremental_update = True

    id = UInt64Field()
    name = StringField()
    parent = ReferenceField("self")

    @classmethod
    def extract(cls, item: "AdministrativeDomainModel"):
        return {
            "id": item.id,
            "name": item.name,
            "parent": item.parent.bi_id if item.parent else 0,
        }
