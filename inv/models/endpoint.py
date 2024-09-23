# ----------------------------------------------------------------------
# Endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Dict

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    IntField,
    EmbeddedDocumentListField,
    ObjectIdField,
)
from mongoengine import signals
from bson import ObjectId

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from .channel import Channel


class UsageItem(EmbeddedDocument):
    """
    Endpoint usage item.

    Attributes:
        channel: Channel reference.
        discriminator: Optional discriminator, if shared.
        direction: Optional direction code.
    """

    channel = PlainReferenceField(Channel)
    discriminator = StringField(required=False)
    direction = IntField(required=False)

    def to_json(self) -> Dict[str, str]:
        r = {
            "channel": str(self.channel.id),
            "channel__label": self.channel.name,
            "name": self.channel.name,
            "discriminator": self.discriminator or "",
        }
        return r


class Endpoint(Document):
    """
    Enpoint.

    Enpoints are resources which
    can be connected together to organize
    channels.


    Attributes:
        channel: Channel reference.
        resource: Resource reference.
        root_resource: Calculated field bound to the nearest inventory object.
        is_rool: Root for p2mp/up2mp topology.
        pair: Pair number for `bunch` topology.
        used_by: List of channels which uses this entrypoint.
    """

    meta = {
        "collection": "endpoints",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["root_resource"],
    }
    channel = PlainReferenceField(Channel, required=True)
    resource = StringField(unique=True)
    root_resource = StringField()
    is_root = BooleanField()
    pair = IntField(required=False)
    used_by = EmbeddedDocumentListField(UsageItem)
    last_job = ObjectIdField(required=False)

    def __str__(self) -> str:
        return f"{self.channel.name}:{self.resource}"

    @classmethod
    def _update_root_resource(cls, sender, document: "Endpoint", **kwargs) -> None:
        """
        Calculate root_resource field.
        """
        if document.resource.count(":") == 1:
            document.root_resource = document.resource
        else:
            parts = document.resource.split(":", 2)
            document.root_resource = f"{parts[0]}:{parts[1]}"

    def set_last_job(self, job_id: ObjectId) -> None:
        """Update last provisioning job id."""
        self.last_job = job_id
        self._get_collection().update_one({"_id": self.id}, {"$set": {"last_job": job_id}})


signals.pre_save.connect(Endpoint._update_root_resource, sender=Endpoint)
