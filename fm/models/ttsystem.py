# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# TTSystem
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
import datetime
import logging
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, ListField, IntField,
                                DateTimeField, BooleanField)
import cachetools
# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.core.handler import get_handler

id_lock = Lock()
logger = logging.getLogger(__name__)

DEFAULT_TTSYSTEM_SHARD = "default"


@on_delete_check(check=[
    ("sa.ManagedObject", "tt_system"),
])
class TTSystem(Document):
    meta = {
        "collection": "noc.ttsystem",
        "strict": False,
        "auto_create_index": False
    }

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
    #
    tags = ListField(StringField())

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return TTSystem.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name):
        t = TTSystem.objects.filter(name=name).first()
        if t:
            return t.get_system()
        else:
            return None

    def get_system(self):
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
        self._get_collection().update({
            "_id": self.id
        }, {
            "$set": {
                "failed_till": d
            }
        })
