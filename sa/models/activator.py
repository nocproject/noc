# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Activator
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
## NOC modules
from activatorcapabilitiescache import ActivatorCapabilitiesCache
from noc.main.models import Shard
from noc.lib.fields import AutoCompleteTagsField
from noc.lib.app.site import site


class Activator(models.Model):
    """
    Activator
    """

    class Meta:
        verbose_name = _("Activator")
        verbose_name_plural = _("Activators")
        db_table = "sa_activator"
        app_label = "sa"
        ordering = ["name"]

    name = models.CharField(_("Name"), max_length=32, unique=True)
    shard = models.ForeignKey(Shard, verbose_name=_("Shard"))
    ip = models.IPAddressField(_("From IP"))
    to_ip = models.IPAddressField(_("To IP"))
    auth = models.CharField(_("Auth String"), max_length=64)
    is_active = models.BooleanField(_("Is Active"), default=True)
    tags = AutoCompleteTagsField(_("Tags"), null=True, blank=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return site.reverse("sa:activator:change", self.id)

    @classmethod
    def check_ip_access(cls, ip):
        """
        Check IP belongs to any activator

        :param ip: IP address
        :type ip: String
        :rtype: Bool
        """
        return Activator.objects.filter(
            ip__gte=ip, to_ip__lte=ip).exists()

    @property
    def capabilities(self):
        """
        Get current activator pool capabilities in form of dict or None
        """
        c = ActivatorCapabilitiesCache.objects.filter(
            activator_id=self.id).first()
        if c is None:
            return {
                "members": 0,
                "max_scripts": 0
            }
        else:
            return {
                "members": c.members,
                "max_scripts": c.max_scripts
            }

    def update_capabilities(self, members, max_scripts):
        """
        Update activator pool capabilities

        :param members: Active members in pool. Pool considered inactive when
                        members == 0
        :param max_scripts: Maximum amount of concurrent scripts in pool
        """
        c = ActivatorCapabilitiesCache.objects.filter(
            activator_id=self.id).first()
        if c:
            c.members = members
            c.max_scripts = max_scripts
            c.save()
        else:
            ActivatorCapabilitiesCache(
                activator_id=self.id,
                members=members,
                max_scripts=max_scripts).save()
