# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AdministrativeDomain
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from threading import RLock
import operator
## Third-party modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
import cachetools
## NOC modules
from noc.main.models.pool import Pool
from noc.core.model.fields import TagsField, DocumentReferenceField


id_lock = RLock()


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

    name = models.CharField(_("Name"), max_length=32, unique=True)
    parent = models.ForeignKey("self", verbose_name="Parent", null=True, blank=True)
    description = models.TextField(
        _("Description"),
        null=True, blank=True)
    default_pool = DocumentReferenceField(
        Pool,
        null=True, blank=True
    )
    tags = TagsField("Tags", null=True, blank=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _path_cache = cachetools.TTLCache(maxsize=100, ttl=60)

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
