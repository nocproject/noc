# ----------------------------------------------------------------------
# Endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, ListField, DateTimeField, EmbeddedDocumentField

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.main.models.label import Label
from .techdomain import TechDomain
from .channel import Channel


class EndpointChannel(EmbeddedDocument):
    """
    Channel to endpoint bindings.

    Attributes:
        channel: Reference to Channel.
        discriminators: List of discriminators.
    """

    channel = PlainReferenceField(Channel, reqired=True)
    discriminators = ListField(StringField())

    def __str__(self) -> str:
        if self.discriminators:
            return f"{self.channel.name}: {'; '.join(self.discriminators)}"
        return self.channel.name


@Label.model
class Endpoint(Document):
    """
    Enpoint.

    Enpoints are entrpypoints which
    can be connected together to organize
    channels.

    Endpoints may be promises. Promise endpoints
    are not exists yet, but may be instlalled later
    whithin defined deadline.

    Attributes:
        tech_domain: Reference to the tech domain.
        name: Human-readable name
        description: Optional description
        model: Name of database model.
        resource_id: Id within database model. Empty for promise.
        slot: Sub-identified within resource.
        effective_labels: List of effective labels.
        deadline: Only for promise endpoints, expected terms
            of the implementation.
        channels: List of connected channels
            channel: Id of the channel.
            discriminators: List of channel's discriminators.
    """

    meta = {
        "collection": "endpoints",
        "strict": False,
        "auto_create_index": False,
        "indexes": [("model", "resource_id")],
    }

    tech_domain = PlainReferenceField(TechDomain, required=True)
    name = StringField(required=True)
    description = StringField()
    model = StringField(required=True)
    resource_id = StringField()
    slot = StringField()
    effective_labels = ListField(StringField())
    deadline = DateTimeField()
    channels = ListField(EmbeddedDocumentField(EndpointChannel))

    def __str__(self) -> str:
        return self.name
