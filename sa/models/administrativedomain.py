# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# AdministrativeDomain
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
import operator

# Third-party modules
import six
from noc.core.translation import ugettext as _
from django.db import models
import cachetools

# NOC modules
from noc.config import config
from noc.core.model.base import NOCModel
from noc.main.models.pool import Pool
from noc.main.models.remotesystem import RemoteSystem
from noc.core.model.fields import TagsField, DocumentReferenceField
from noc.core.model.decorator import on_delete_check, on_init
from noc.core.bi.decorator import bi_sync
from noc.core.datastream.decorator import datastream

id_lock = Lock()
_path_cache = cachetools.TTLCache(maxsize=1000, ttl=60)


@on_init
@bi_sync
@datastream
@on_delete_check(
    check=[
        ("cm.ObjectNotify", "administrative_domain"),
        # ("fm.EscalationItem", "administrative_domain"),
        ("sa.GroupAccess", "administrative_domain"),
        ("sa.ManagedObject", "administrative_domain"),
        ("sa.ManagedObjectSelector", "filter_administrative_domain"),
        ("sa.UserAccess", "administrative_domain"),
        ("sa.AdministrativeDomain", "parent"),
        ("phone.PhoneNumber", "administrative_domain"),
        ("phone.PhoneRange", "administrative_domain"),
    ]
)
@six.python_2_unicode_compatible
class AdministrativeDomain(NOCModel):
    """
    Administrative Domain
    """

    class Meta(object):
        verbose_name = _("Administrative Domain")
        verbose_name_plural = _("Administrative Domains")
        db_table = "sa_administrativedomain"
        app_label = "sa"
        ordering = ["name"]

    name = models.CharField(_("Name"), max_length=255, unique=True)
    parent = models.ForeignKey(
        "self", verbose_name="Parent", null=True, blank=True, on_delete=models.CASCADE
    )
    description = models.TextField(_("Description"), null=True, blank=True)
    default_pool = DocumentReferenceField(Pool, null=True, blank=True)
    # Integration with external NRI systems
    # Reference to remote system object has been imported from
    remote_system = DocumentReferenceField(RemoteSystem, null=True, blank=True)
    # Object id in remote system
    remote_id = models.CharField(max_length=64, null=True, blank=True)
    # Object id in BI
    bi_id = models.BigIntegerField(unique=True)

    tags = TagsField("Tags", null=True, blank=True)

    _id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _nested_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        ad = AdministrativeDomain.objects.filter(id=id)[:1]
        if ad:
            return ad[0]
        return None

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id):
        ad = AdministrativeDomain.objects.filter(bi_id=id)[:1]
        if ad:
            return ad[0]
        return None

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_administrativedomain:
            yield "administrativedomain", self.id

    @cachetools.cached(_path_cache, key=lambda s: s.id, lock=id_lock)
    def get_path(self):
        """
        Returns list of parent administrative domain ids
        :return:
        """
        if self.parent:
            return self.parent.get_path() + [self.id]
        return [self.id]

    def get_default_pool(self):
        if self.default_pool:
            return self.default_pool
        if self.parent:
            return self.parent.get_default_pool()
        return None

    def get_nested(self):
        """
        Returns list of nested administrative domains
        :return:
        """
        r = [self]
        for d in AdministrativeDomain.objects.filter(parent=self):
            r += d.get_nested()
        return r

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_nested_cache"), lock=lambda _: id_lock)
    def get_nested_ids(cls, administrative_domain):
        from django.db import connection

        if hasattr(administrative_domain, "id"):
            administrative_domain = administrative_domain.id
        cursor = connection.cursor()
        cursor.execute(
            """
            WITH RECURSIVE r AS (
                 SELECT id, parent_id
                 FROM sa_administrativedomain
                 WHERE id = %d
                 UNION
                 SELECT ad.id, ad.parent_id
                 FROM sa_administrativedomain ad JOIN r ON ad.parent_id = r.id
            )
            SELECT id FROM r
        """
            % administrative_domain
        )
        return [r[0] for r in cursor]

    @property
    def has_children(self):
        return True if AdministrativeDomain.objects.filter(parent=self.id) else False
