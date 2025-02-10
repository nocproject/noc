# ----------------------------------------------------------------------
# Channel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional, Union
import operator


# Third-party modules
from bson import ObjectId
import cachetools
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    LongField,
    ListField,
    BooleanField,
    EmbeddedDocumentListField,
)

# NOC modules
from noc.core.bi.decorator import bi_sync
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.project.models.project import Project
from noc.crm.models.subscriber import Subscriber
from noc.crm.models.supplier import Supplier
from noc.main.models.label import Label
from noc.main.models.remotesystem import RemoteSystem
from noc.core.model.decorator import on_delete_check
from noc.core.channel.types import ChannelKind, ChannelTopology
from .techdomain import TechDomain

id_lock = Lock()


class ConstraintItem(EmbeddedDocument):
    """
    Constraint Item.

    Attributes:
        type: Constraint type, include of exclude.
        strict: Generate fault if constraint cannot be met.
        resource: Resource reference.
    """

    type = StringField(choices=["i", "e"])
    strict = BooleanField()
    resource = StringField()


class ParamItem(EmbeddedDocument):
    name = StringField()
    value = StringField()


@bi_sync
@Label.model
@on_delete_check(check=[("inv.Channel", "parent"), ("inv.Endpoint", "channel")])
class Channel(Document):
    """
    Channel.
    """

    meta = {
        "collection": "channels",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["effective_labels"],
    }

    name = StringField(unique=True)
    parent = PlainReferenceField("self", allow_blank=True)
    tech_domain = PlainReferenceField(TechDomain)
    description = StringField()
    project = ForeignKeyField(Project)
    supplier = PlainReferenceField(Supplier)
    subscriber = PlainReferenceField(Subscriber)
    kind = StringField(choices=[x.value for x in ChannelKind])
    topology = StringField(choices=[x.value for x in ChannelTopology])
    discriminator = StringField(required=False)
    labels = ListField(StringField())
    effective_labels = ListField(StringField())
    constraints = EmbeddedDocumentListField(ConstraintItem)
    params = EmbeddedDocumentListField(ParamItem)
    # Controller which created the channel
    controller = StringField(required=False)
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = PlainReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self) -> str:
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["Channel"]:
        return Channel.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["Channel"]:
        return Channel.objects.filter(bi_id=bi_id).first()

    @property
    def is_unidirectional(self) -> bool:
        """
        Check if channel is unidirectional.
        """
        return self.topology in (
            ChannelTopology.UP2P.value,
            ChannelTopology.UBUNCH.value,
            ChannelTopology.UP2MP.value,
        )

    def on_before_delete(self) -> None:
        """
        Perform checks and clean up endpoints.
        """
        from .endpoint import Endpoint

        # Check channel is not used by other channels
        used = set()
        for ep in Endpoint.objects.filter(channel=self.id):
            if ep.used_by:
                for item in ep.used_by:
                    used.add(item.channel.name)
        if used:
            if len(used) <= 3:
                msg = f"Channel is used by: {', '.join(used)}"
            else:
                msg = f"Channel is used by {len(used)} channels"
            raise ValueError(msg)

        # Remove endpoints
        Endpoint.objects.filter(channel=self.id).delete()

        # Remove from used_by
        for ep in Endpoint.objects.filter(used_by__channel=self.id):
            ep.used_by = [i for i in ep.used_by if i.channel.id != self.id]
            ep.save()

    def update_params(self, **kwargs: dict[str, str | None]) -> bool:
        """
        Update channel parameters.

        Save when necessary.

        Returns:
            True: If channel has been modified.
            False: No changes.
        """
        changed = False
        new_params: list[ParamItem] = []
        # Update/Delete
        for item in self.params or []:
            new_value = kwargs.get(item.name)
            if new_value:
                if new_value != item.value:
                    changed = True
                new_params.append(ParamItem(name=item.name, value=new_value))
            else:
                changed = True  # Skip
        # Insert
        for name in set(kwargs) - {item.name for item in self.params or []}:
            if kwargs[name]:
                new_params.append(ParamItem(name=name, value=kwargs[name]))
                changed = True
        if changed:
            self.params = new_params
            self.save()
