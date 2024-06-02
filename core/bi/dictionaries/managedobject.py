# ----------------------------------------------------------------------
# ManagedObject dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import DictionaryModel
from noc.core.clickhouse.fields import StringField, UInt64Field
from noc.sa.models.managedobject import ManagedObject as ManagedObjectModel
from noc.core.text import ch_escape


class ManagedObject(DictionaryModel):
    class Meta(object):
        name = "managedobject"
        layout = "hashed"
        source_model = "sa.ManagedObject"
        incremental_update = True

    name = StringField()
    id = UInt64Field()
    address = StringField()
    profile = StringField()
    platform = StringField()
    version = StringField()
    remote_id = StringField()
    remote_system = StringField()
    administrative_domain = StringField()
    administrative_domain_id = StringField()
    location_address = StringField()
    project = StringField()

    @classmethod
    def extract(cls, item: "ManagedObjectModel"):
        return {
            "id": item.id,
            "name": ch_escape(item.name),
            "address": item.address,
            "profile": item.profile.name,
            "platform": ch_escape(item.platform.name if item.platform else ""),
            "version": ch_escape(item.version.version if item.version else ""),
            "remote_id": item.remote_id or "",
            "remote_system": item.remote_system.name if item.remote_system else "",
            "administrative_domain_id": str(item.administrative_domain.id),
            "administrative_domain": item.administrative_domain.name,
            "location_address": (
                item.container.get_data("address", "text") if item.container else ""
            ),
            "project": item.project.name if item.project else "",
        }
