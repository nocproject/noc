# ---------------------------------------------------------------------
# TTSystem
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import Optional, Union
import datetime
import logging

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import (
    StringField,
    ListField,
    IntField,
    ReferenceField,
    DateTimeField,
    BooleanField,
)
import cachetools

# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.core.handler import get_handler
from noc.core.tt.base import BaseTTSystem
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.label import Label

id_lock = Lock()
logger = logging.getLogger(__name__)

DEFAULT_TTSYSTEM_SHARD = "default"


@Label.match_labels("ttsystem", allowed_op={"="})
@on_delete_check(
    check=[("sa.ManagedObject", "tt_system")],
    clean_lazy_labels="ttsystem",
)
class TTSystem(Document):
    meta = {"collection": "noc.ttsystem", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    #
    is_active = BooleanField(default=False)
    # Full path to BaseTTSystem instance
    handler = StringField()
    description = StringField()
    # Connection string
    connection = StringField()
    # Failure condition checking
    failure_cooldown = IntField(default=0)
    failed_till = DateTimeField()
    # Threadpool settings
    shard_name = StringField(default=DEFAULT_TTSYSTEM_SHARD)
    max_threads = IntField(default=10)
    # Telemetry settings
    telemetry_sample = IntField(default=0)
    # Escalation Policy settings
    alarm_consequence_policy = StringField(
        required=True,
        choices=[
            ("D", "Disable"),
            ("a", "Escalate with alarm timestamp"),
            ("c", "Escalate with current timestamp"),
        ],
        default="a",
    )
    #
    tags = ListField(StringField())
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = ReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["TTSystem"]:
        return TTSystem.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name):
        return TTSystem.objects.filter(name=name).first()

    def save(self, *args, **kwargs):
        from noc.core.cache.base import cache
        from noc.sa.models.managedobject import ManagedObject, MANAGEDOBJECT_CACHE_VERSION

        # After save changed_fields will be empty
        super().save(*args, **kwargs)

        # Invalidate ManagedObject cache
        deleted_cache_keys = [
            "managedobject-id-%s" % mo_id
            for mo_id in ManagedObject.objects.filter(tt_system=self.id).values_list(
                "id", flat=True
            )
        ]
        cache.delete_many(deleted_cache_keys, version=MANAGEDOBJECT_CACHE_VERSION)

    def get_system(self) -> BaseTTSystem:
        """
        Return BaseTTSystem instance
        """
        h = get_handler(self.handler)
        if not h:
            raise ValueError
        return h(self.name, self.connection)

    def is_failed(self):
        """
        Check TTSystem is in failed state
        :return:
        """
        if not self.failed_till:
            return False
        now = datetime.datetime.now()
        return now <= self.failed_till

    def register_failure(self):
        cooldown = self.failure_cooldown
        if not cooldown:
            return
        d = datetime.datetime.now() + datetime.timedelta(seconds=cooldown)
        logger.info("[%s] Setting failure status till %s", self.name, d)
        self._get_collection().update_one({"_id": self.id}, {"$set": {"failed_till": d}})

    @classmethod
    def iter_lazy_labels(cls, ttsystem: "TTSystem"):
        yield f"noc::ttsystem::{ttsystem.name}::="
