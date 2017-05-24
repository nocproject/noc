# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DNSZoneProfile model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
# NOC modules
from dnsserver import DNSServer
from noc.main.models import NotificationGroup


class DNSZoneProfile(models.Model):
    """
    DNS Zone profile is a set of common parameters, shared between zones.

    :param name:
    :param masters:
    :param slaves:
    :param zone_soa:
    :param zone_contact:
    :param zone_refresh:
    :param zone_retry:
    :param zone_expire:
    :param zone_ttl:
    :param notification_group:
    :param description:
    """
    class Meta:
        verbose_name = _("DNS Zone Profile")
        verbose_name_plural = _("DNS Zone Profiles")
        db_table = "dns_dnszoneprofile"
        app_label = "dns"

    name = models.CharField(_("Name"), max_length=32, unique=True)
    masters = models.ManyToManyField(DNSServer, verbose_name=_("Masters"),
        related_name="masters", blank=True)
    slaves = models.ManyToManyField(DNSServer, verbose_name=_("Slaves"),
        related_name="slaves", blank=True)
    zone_soa = models.CharField(_("SOA"), max_length=64)
    zone_contact = models.CharField(_("Contact"), max_length=64)
    zone_refresh = models.IntegerField(_("Refresh"), default=3600)
    zone_retry = models.IntegerField(_("Retry"), default=900)
    zone_expire = models.IntegerField(_("Expire"), default=86400)
    zone_ttl = models.IntegerField(_("TTL"), default=3600)
    notification_group = models.ForeignKey(NotificationGroup,
        verbose_name=_("Notification Group"), null=True, blank=True,
        help_text=_("Notification group to use when zone group is not set"))
    description = models.TextField(_("Description"), blank=True, null=True)

    def __unicode__(self):
        return self.name

    @property
    def authoritative_servers(self):
        """
        Returns a list of DNSServer instances for all zone's master and
        slave servers
        """
        return list(self.masters.all()) + list(self.slaves.all())

#
# Signal handlers
#
@receiver(post_save, sender=DNSZoneProfile)
def on_save(sender, instance, created, **kwargs):
    for z in instance.dnszone_set.filter(is_auto_generated=True):
        z.touch(z.name)
