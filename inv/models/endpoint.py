# ----------------------------------------------------------------------
# Endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, ListField

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.main.models.label import Label
from .techdomain import TechDomain
from .channel import Channel


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
        channels: Connected channel
    """

    meta = {
        "collection": "endpoints",
        "strict": False,
        "auto_create_index": False,
        "indexes": [("model", "resource_id", "slot"), "channel", "effective_labels"],
    }
    name = StringField(required=True)
    description = StringField()
    channel = PlainReferenceField(Channel, required=True)
    tech_domain = PlainReferenceField(TechDomain, required=True)
    model = StringField(required=True)
    resource_id = StringField()
    slot = StringField(required=False)
    discriminator = StringField(required=False)
    labels = ListField(StringField())
    effective_labels = ListField(StringField())

    def __str__(self) -> str:
        return self.name
