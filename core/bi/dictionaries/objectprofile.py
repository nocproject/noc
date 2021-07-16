# ----------------------------------------------------------------------
# ObjectProfile dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import DictionaryModel
from noc.core.clickhouse.fields import StringField, UInt16Field, BooleanField
from noc.sa.models.managedobjectprofile import ManagedObjectProfile


class ObjectProfile(DictionaryModel):
    class Meta(object):
        name = "objectprofile"
        layout = "hashed"
        source_model = "sa.ManagedObjectProfile"
        incremental_update = True

    id = StringField()
    name = StringField()
    # ObjectProfile Level
    level = UInt16Field()
    enable_ping = BooleanField()
    enable_box_discovery = BooleanField()
    enable_periodic_discovery = BooleanField()

    @classmethod
    def extract(cls, item: "ManagedObjectProfile"):
        return {
            "id": str(item.id),
            "name": item.name,
            "level": item.level,
            "enable_ping": int(item.enable_ping or 0),
            "enable_box_discovery": int(item.enable_box_discovery or 0),
            "enable_periodic_discovery": int(item.enable_periodic_discovery or 0),
        }
