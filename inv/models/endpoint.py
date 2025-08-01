# ----------------------------------------------------------------------
# Endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, List

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    IntField,
    EmbeddedDocumentListField,
    ListField,
)
from mongoengine import signals

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.model.decorator import on_delete
from noc.core.resource import from_resource, resource_label, resource_path
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

    def to_json(self) -> dict[str, str]:
        r = {
            "channel": str(self.channel.id),
            "channel__label": self.channel.name,
            "name": self.channel.name,
            "discriminator": self.discriminator or "",
        }
        return r


class ConstraintItem(EmbeddedDocument):
    name = StringField()
    values = ListField(StringField())

    def __str__(self) -> str:
        return f"{self.name} = [{', '.join(v for v in self.values)}]"

    def to_json(self) -> dict[str, Any]:
        return {"name": self.name, "values": [x for x in self.values]}


@on_delete
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
        constraints: Pair constraints.
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
    constraints = EmbeddedDocumentListField(ConstraintItem, required=False)

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

    def on_delete(self):
        """Clean up endpoint."""
        from noc.core.techdomain.profile.channel import ProfileChannelController

        if not self.channel.controller or not self.resource.startswith("o:"):
            return  # Not managed
        # Resolve object
        obj, _ = from_resource(self.resource)
        if not obj:
            return
        # Get controller
        ctl = ProfileChannelController.get_controller_for_object(obj, self.channel.controller)
        if not ctl:
            return
        # Start cleanup job
        job = ctl.cleanup(self)
        if job:
            job.submit()

    @property
    def resource_label(self) -> str:
        """Human-readable label for resource."""
        return resource_label(self.resource)

    @property
    def resource_path(self) -> list[str] | None:
        """Resource path."""
        return resource_path(self.resource)

    def as_resource_path(self) -> List[str]:
        """Convert to resource path."""
        return [self.channel.as_resource(), self.resource]


signals.pre_save.connect(Endpoint._update_root_resource, sender=Endpoint)
