# ---------------------------------------------------------------------
# Peer Profile model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from functools import partial
from typing import Optional, Dict, List, Any

# Third-party modules
import cachetools
from django.db.models import CharField, IntegerField
from pydantic import BaseModel, RootModel

# NOC modules
from noc.core.model.base import NOCModel
from noc.core.model.fields import DocumentReferenceField, PydanticField
from noc.core.model.decorator import on_delete_check, on_init
from noc.wf.models.workflow import Workflow
from noc.core.change.decorator import change

id_lock = Lock()


class ModelDataItem(BaseModel):
    name: str
    value: Any
    source: str = "manual"

    def __str__(self):
        return f"{self.name}: {self.value}"


DataItems = RootModel[List[ModelDataItem]]


@on_init
@change
@on_delete_check(check=[("peer.Peer", "profile")])
class PeerProfile(NOCModel):
    class Meta(object):
        verbose_name = "Peer Profile"
        verbose_name_plural = "Peer Profiles"
        db_table = "peer_peerprofile"
        app_label = "peer"

    name = CharField("Name", max_length=32, unique=True)
    description = CharField("Description", max_length=64)
    # Allow Type ?
    workflow: "Workflow" = DocumentReferenceField(
        Workflow,
        null=False,
        blank=False,
        default=partial(Workflow.get_default_workflow, "peer.PeerProfile"),
    )
    max_prefixes = IntegerField("Max. Prefixes", default=100)
    data: List[Dict[str, str]] = PydanticField(
        "Data Items",
        schema=DataItems,
        blank=True,
        null=True,
        default=list,
        # ? Internal validation not worked with JSON Field
        # validators=[match_rules_validate],
    )
    # generate_rpsl = BooleanField(default=False)
    # Discovery
    status_discovery = CharField(
        choices=[
            ("d", "Disabled"),
            ("e", "Enable"),
            ("c", "Clear Alarm"),
            ("ca", "Clear Alarm if Admin Down"),
            ("rc", "Raise & Clear Alarm"),
        ],
        default="d",
        max_length=2,
    )
    # Send up/down notifications
    status_change_notification = CharField(
        choices=[
            ("d", "Disabled"),
            ("c", "Changed Message"),
            ("f", "All Message"),
        ],
        default="d",
        max_length=1,
    )

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _default_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    DEFAULT_PROFILE_NAME = "default"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id: int) -> Optional["PeerProfile"]:
        return PeerProfile.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_default_cache"), lock=lambda _: id_lock)
    def get_default_profile(cls) -> "PeerProfile":
        return PeerProfile.objects.filter(name=cls.DEFAULT_PROFILE_NAME).first()

    def get_effective_data(self) -> Dict[str, Any]:
        r = {}
        for d in self.data:
            r[d["name"]] = d["value"]
        return r

    def get_data(self, name: str) -> Optional[Any]:
        for d in self.data:
            if d["name"] == name:
                return d["value"]
