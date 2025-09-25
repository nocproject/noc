# ----------------------------------------------------------------------
# Version dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import DictionaryModel
from noc.core.clickhouse.fields import StringField
from noc.inv.models.firmware import Firmware
from noc.core.text import ch_escape


class Version(DictionaryModel):
    class Meta(object):
        name = "version"
        layout = "hashed"
        source_model = "inv.Firmware"
        incremental_update = True

    id = StringField()
    name = StringField()
    profile = StringField()
    vendor = StringField()

    @classmethod
    def extract(cls, item: "Firmware"):
        return {
            "id": str(item.id),
            "name": ch_escape(item.version),
            "profile": ch_escape(item.profile.name if item.profile else ""),
            "vendor": item.vendor.name if item.vendor else "",
        }
