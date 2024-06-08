# ----------------------------------------------------------------------
# Service dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import DictionaryModel
from noc.core.clickhouse.fields import StringField, UInt32Field, ReferenceField
from noc.sa.models.service import Service as ServiceModel


class Service(DictionaryModel):
    class Meta(object):
        name = "service"
        layout = "hashed"
        source_model = "sa.Service"
        incremental_update = True

    id = StringField()
    profile = StringField()
    parent = ReferenceField("self")
    supplier = StringField()
    description = StringField()
    agreement_id = StringField()
    address = StringField()
    glyph = StringField()
    bandwidth = UInt32Field()
    endpoint_ip = StringField()
    division_code = StringField()

    @classmethod
    def extract(cls, item: "ServiceModel"):
        caps = item.get_caps()
        return {
            "id": str(item.id),
            "profile": item.profile.name,
            "parent": item.parent.bi_id if item.parent else 0,
            "supplier": item.supplier.name if item.supplier else "",
            "description": item.description or "",
            "agreement_id": item.agreement_id or "",
            "address": item.address or "",
            "glyph": item.profile.glyph or "",
            "bandwidth": int(caps.get("Channel | Bandwidth", 0)),
            "endpoint_ip": caps.get("Channel | Address", ""),
            "division_code": caps.get("Channel | Division | Code", ""),
        }
