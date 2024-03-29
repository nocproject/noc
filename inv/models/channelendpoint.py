# ----------------------------------------------------------------------
# ChannelEndpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, ListField

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from .endpoint import Endpoint
from .channel import Channel


class ChannelEndpoint(Document):
    meta = {
        "collection": "channelendpoints",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["tech_domain", "channel", "endpoint"],
    }
    endpoint = PlainReferenceField(Endpoint)
    channel = PlainReferenceField(Channel)
    discriminator = StringField(required=False)

    def __str__(self) -> str:
        if self.discriminator:
            return f"{self.channel.name}: {self.endpoint.name}"
        return f"{self.channel.name}: {self.endpoint.name} ({self.discriminator})"
