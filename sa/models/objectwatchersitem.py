# ---------------------------------------------------------------------
# ObjectWatch model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional

# Third-party modules
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import EnumField, StringField, BooleanField, DictField, DateTimeField

# NOC Modules
from noc.core.watchers.types import ObjectEffect, WatchItem
from noc.core.mongo.fields import PlainReferenceField
from noc.main.models.remotesystem import RemoteSystem


class WatchDocumentItem(EmbeddedDocument):
    """
    Attributes:
        effect: Watch Effect
        key: Id for action Instance
        once: Run only once
        args: Addition options for run
    """

    meta = {"strict": False, "auto_create_index": False}

    effect: ObjectEffect = EnumField(ObjectEffect, required=True)
    # Match, Array
    key = StringField(required=False)
    after = DateTimeField(required=False)
    once: bool = BooleanField(default=True)
    # action: ActionType = EnumField(ActionType, required=False)
    # Action
    remote_system = PlainReferenceField(RemoteSystem)
    args = DictField()

    def __str__(self):
        return f"{self.effect}:{self.key}"

    @property
    def item(self) -> "WatchItem":
        """"""
        return WatchItem(
            effect=self.effect,
            key=self.key,
            after=self.after,
            once=self.once,
            remote_system=self.remote_system,
            args=self.args,
        )

    @classmethod
    def from_item(cls, item: WatchItem, remote_system: Optional[RemoteSystem] = None):
        """Create record from WatchItem"""
        return WatchDocumentItem(
            effect=item.effect,
            key=item.key,
            remote_system=item.remote_system or remote_system,
            after=item.after,
            once=item.once,
            args=item.args,
        )
