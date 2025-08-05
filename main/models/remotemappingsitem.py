# ----------------------------------------------------------------------
# RemoteMapping Item
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import StringField

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from .remotesystem import RemoteSystem


class RemoteMappingItem(EmbeddedDocument):
    """source priority: m - manual, e - etl, o - other"""

    meta = {"strict": False, "auto_create_index": False}

    remote_system: RemoteSystem = PlainReferenceField(RemoteSystem, required=True)
    remote_id: str = StringField(required=True)
    sources: str = StringField(default="o")

    def __str__(self):
        return f"{self.remote_system.name}@{self.remote_id} ({''.join(self.sources)})"
