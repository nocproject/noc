# ----------------------------------------------------------------------
# platform dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import DictionaryModel
from noc.core.clickhouse.fields import StringField
from noc.inv.models.platform import Platform as PlatformModel
from noc.core.text import ch_escape


class Platform(DictionaryModel):
    class Meta(object):
        name = "platform"
        layout = "hashed"
        source_model = "inv.Platform"
        incremental_update = True

    id = StringField()
    # Platform name
    name = StringField()
    # Vendor name
    vendor = StringField()
    # <vendor> <platdorm>
    full_name = StringField()

    @classmethod
    def extract(cls, item: "PlatformModel"):
        return {
            "id": str(item.id),
            "name": ch_escape(item.name),
            "vendor": item.vendor.name if item.vendor else "",
            "full_name": ch_escape(item.full_name),
        }
