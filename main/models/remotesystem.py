# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# RemoteSystem model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, ListField,
                                EmbeddedDocumentField, BooleanField,
                                DateTimeField)
import cachetools
# NOC modules
from noc.core.handler import get_handler

id_lock = Lock()

class EnvItem(EmbeddedDocument):
    """
    Environment item
    """
    key = StringField()
    value = StringField()

    def __unicode__(self):
        return self.key


class RemoteSystem(Document):
    meta = {
        "collection": "noc.remotesystem",
        "allow_inheritance": False
    }

    name = StringField(unique=True)
    description = StringField()
    handler = StringField()
    # Environment variables
    environment = ListField(EmbeddedDocumentField(EnvItem))
    # Enable extractors/loaders
    enable_admdiv = BooleanField()
    enable_administrativedomain = BooleanField()
    enable_authprofile = BooleanField()
    enable_container = BooleanField()
    enable_link = BooleanField()
    enable_managedobject = BooleanField()
    enable_managedobjectprofile = BooleanField()
    enable_networksegment = BooleanField()
    enable_service = BooleanField()
    enable_subscriber = BooleanField()
    enable_terminationgroup = BooleanField()
    enable_ttsystem = BooleanField()
    enable_ttmap = BooleanField()
    # Usage statistics
    last_extract = DateTimeField()
    last_successful_extract = DateTimeField()
    extract_error = StringField()
    last_load = StringField()
    last_successful_load = DateTimeField()
    load_error = StringField()

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"),
                             lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return RemoteSystem.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"),
                             lock=lambda _: id_lock)
    def get_by_name(cls, name):
        return RemoteSystem.objects.filter(name=name).first()

    @property
    def config(self):
        if not hasattr(self, "_config"):
            self._config = dict((e.key, e.value)
                                for e in self.environment)
        return self._config

    def get_handler(self):
        """
        Return BaseTTSystem instance
        """
        h = get_handler(str(self.handler))
        if not h:
            raise ValueError
        return h(self)

    def get_extractors(self):
        extractors = []
        for k in self._meta.fields:
            if k.startwith("enable_") and getattr(self, k):
                extractors += [k[7:]]
        return extractors

    def extract(self, extractors=None):
        extractors = extractors or self.get_extractors()
        self.get_handler().extract(extractors)

    def load(self, extractors=None):
        extractors = extractors or self.get_extractors()
        self.get_handler().load(extractors)
