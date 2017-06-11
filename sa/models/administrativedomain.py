# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# AdministrativeDomain
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
# Third-party modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
import cachetools
# NOC modules
from noc.main.models.pool import Pool
from noc.main.models.remotesystem import RemoteSystem
from noc.core.model.fields import TagsField, DocumentReferenceField
from noc.core.model.decorator import on_delete_check


id_lock = Lock()


@on_delete_check(check=[
    ("cm.ObjectNotify", "administrative_domain"),
    # ("fm.EscalationItem", "administrative_domain"),
    ("sa.GroupAccess", "administrative_domain"),
    ("sa.ManagedObject", "administrative_domain"),
    ("sa.ManagedObjectSelector", "filter_administrative_domain"),
    ("sa.UserAccess", "administrative_domain"),
    ("sa.AdministrativeDomain", "parent")
])
class AdministrativeDomain(models.Model):
    """
    Administrative Domain
    """
    class Meta:
        verbose_name = _("Administrative Domain")
        verbose_name_plural = _("Administrative Domains")
        db_table = "sa_administrativedomain"
        app_label = "sa"
        ordering = ["name"]

    name = models.CharField(_("Name"), max_length=255, unique=True)
    parent = models.ForeignKey("self", verbose_name="Parent", null=True, blank=True)
    description = models.TextField(
        _("Description"),
        null=True, blank=True)
    default_pool = DocumentReferenceField(
        Pool,
        null=True, blank=True
    )
    # Integration with external NRI systems
    # Reference to remote system object has been imported from
    remote_system = DocumentReferenceField(RemoteSystem,
                                           null=True, blank=True)
    # Object id in remote system
    remote_id = models.CharField(max_length=64, null=True, blank=True)
    # Object id in BI
    bi_id = models.DecimalField(max_digits=20, decimal_places=0, null=True, blank=True)

    tags = TagsField("Tags", null=True, blank=True)

    _id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _path_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _nested_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        try:
            return AdministrativeDomain.objects.get(id=id)
        except AdministrativeDomain.DoesNotExist:
            return None

    @cachetools.cachedmethod(operator.attrgetter("_path_cache"), lock=lambda _: id_lock)
    def get_path(self):
        """
        Returns list of parent segment ids
        :return:
        """
        if self.parent:
            return self.parent.get_path() + [self.id]
        else:
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
        cursor.execute("""
            WITH RECURSIVE r AS (
                 SELECT id, parent_id
                 FROM sa_administrativedomain
                 WHERE id = %d
                 UNION
                 SELECT ad.id, ad.parent_id
                 FROM sa_administrativedomain ad JOIN r ON ad.parent_id = r.id
            )
            SELECT id FROM r
        """ % administrative_domain)
        return [r[0] for r in cursor]

    @property
    def has_children(self):
        return True if AdministrativeDomain.objects.filter(parent=self.id) else False
