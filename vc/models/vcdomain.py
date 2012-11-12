# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VCDomain model
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## NOC modules
from vctype import VCType
from vcfilter import VCFilter
from noc.main.models import Style
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.sa.models.selectorcache import SelectorCache


class VCDomain(models.Model):
    """
    Virtual circuit domain, allows to separate unique VC spaces
    """
    class Meta:
        verbose_name = "VC Domain"
        verbose_name_plural = "VC Domains"
        db_table = "vc_vcdomain"
        app_label = "vc"

    name = models.CharField("Name", max_length=64, unique=True)
    description = models.TextField("Description", blank=True, null=True)
    type = models.ForeignKey(VCType, verbose_name="Type")
    enable_provisioning = models.BooleanField(
        "Enable Provisioning", default=False)
    enable_vc_bind_filter = models.BooleanField(
        "Enable VC Bind filter", default=False)
    selector = models.ForeignKey(
        ManagedObjectSelector,
        verbose_name="Selector",
        null=True, blank=True)
    style = models.ForeignKey(
        Style,
        verbose_name="Style",
        blank=True, null=True)

    def __unicode__(self):
        return self.name

    @classmethod
    def get_for_object(cls, managed_object):
        """
        Find VC Domain for Managed Object
        :param managed_object: Managed Object instance
        :return: VC Domain instance or None
        """
        c = SelectorCache.objects.filter(object=managed_object.id,
            vc_domain__ne=None).first()
        if not c:
            return None  # No cached entry found
        if not c.vc_domain:
            return None  # No assotiated domain
        try:
            return cls.objects.get(id=c.vc_domain)
        except cls.DoesNotExist:
            return None  # Record not found

    def get_free_label(self, vc_filter=None):
        """
        Find free label in VC Domain
        :param vc_filter: Optional VC Filter to restrict labels
        :type vc_filter: VCFilter
        :returns: Free label or None
        :rtype: int or None
        """
        l_min = self.type.label1_min
        l_max = self.type.label1_max
        # Get valid ranges
        if vc_filter is None:
            chunks = [(l_min, l_max)]  # No filter
        else:
            chunks = VCFilter.compile(vc_filter.expression)
        # Find first free
        for x, y in chunks:
            if x > y or y < l_min or x > l_max:
                continue  # Skip chunk outside of type's range
            for l in range(max(l_min, x), min(l_max, y) + 1):
                if not VC.objects.filter(vc_domain=self, l1=l).exists():
                    return l  # Return first free found
        return None  # Nothing found

## Avoid circular references
from vc import VC
