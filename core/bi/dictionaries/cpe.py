# ----------------------------------------------------------------------
# CPE Attributes dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import DictionaryModel
from noc.core.clickhouse.fields import StringField
from noc.sa.models.cpestatus import CPEStatus
from noc.core.text import ch_escape


class CPEAttributes(DictionaryModel):
    class Meta(object):
        name = "cpe"
        layout = "complex_key_hashed"
        source_model = "sa.CPEStatus"
        primary_key = ("bi_id", "cpe_id")
        incremental_update = True

    cpe_id = StringField()
    interface = StringField()
    local_id = StringField()
    global_id = StringField()
    name = StringField()
    type = StringField()
    vendor = StringField()
    model = StringField()
    version = StringField()
    serial = StringField()
    ip = StringField()
    mac = StringField()
    description = StringField()
    location = StringField()
    distance = StringField()

    @classmethod
    def extract(cls, item: "CPEStatus"):
        return {
            "bi_id": item.managed_object.bi_id,
            "cpe_id": item.global_id,
            "interface": item.interface,
            "local_id": ch_escape(item.local_id),
            "global_id": ch_escape(item.global_id),
            "name": ch_escape(item.name),
            "type": item.type,
            "vendor": item.vendor,
            "model": ch_escape(item.model),
            "version": item.version,
            "serial": ch_escape(item.serial),
            "ip": item.ip,
            "mac": item.mac,
            "description": ch_escape(item.description),
            "location": ch_escape(item.location),
            "distance": item.distance,
        }
