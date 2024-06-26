# ----------------------------------------------------------------------
# Endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    IntField,
    EmbeddedDocumentListField,
)

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


class Endpoint(Document):
    """
    Enpoint.

    Enpoints are resources which
    can be connected together to organize
    channels.


    Attributes:
        channel: Channel reference.
        resource: Resource reference.
        is_rool: Root for p2mp/up2mp topology.
        pair: Pair number for `bunch` topology.
        used_by: List of channels which uses this entrypoint.
    """

    meta = {
        "collection": "endpoints",
        "strict": False,
        "auto_create_index": False,
    }
    channel = PlainReferenceField(Channel, required=True)
    resource = StringField(unique=True)
    is_root = BooleanField()
    pair = IntField(required=False)
    used_by = EmbeddedDocumentListField(UsageItem)

    def __str__(self) -> str:
        return self.name
