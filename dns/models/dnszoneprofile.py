# ---------------------------------------------------------------------
# DNSZoneProfile model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional
import operator

# Third-party modules
from django.db import models
import cachetools

# NOC modules
from noc.config import config
from noc.core.model.base import NOCModel
from noc.core.model.decorator import on_init
from noc.main.models.notificationgroup import NotificationGroup
from noc.core.change.decorator import change
from noc.core.model.decorator import on_delete_check
from noc.core.translation import ugettext as _
from .dnsserver import DNSServer

id_lock = Lock()


@on_init
@change
@on_delete_check(check=[("dns.DNSZone", "profile")])
class DNSZoneProfile(NOCModel):
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

    class Meta(object):
        verbose_name = _("DNS Zone Profile")
        verbose_name_plural = _("DNS Zone Profiles")
        db_table = "dns_dnszoneprofile"
        app_label = "dns"

    name = models.CharField(_("Name"), max_length=32, unique=True)
    masters = models.ManyToManyField(
        DNSServer, verbose_name=_("Masters"), related_name="masters", blank=True
    )
    slaves = models.ManyToManyField(
        DNSServer, verbose_name=_("Slaves"), related_name="slaves", blank=True
    )
    zone_soa = models.CharField(_("SOA"), max_length=64)
    zone_contact = models.CharField(_("Contact"), max_length=64)
    zone_refresh = models.IntegerField(_("Refresh"), default=3600)
    zone_retry = models.IntegerField(_("Retry"), default=900)
    zone_expire = models.IntegerField(_("Expire"), default=86400)
    zone_ttl = models.IntegerField(_("TTL"), default=3600)
    notification_group = models.ForeignKey(
        NotificationGroup,
        verbose_name=_("Notification Group"),
        null=True,
        blank=True,
        help_text=_("Notification group to use when zone group is not set"),
        on_delete=models.CASCADE,
    )
    description = models.TextField(_("Description"), blank=True, null=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id: int) -> Optional["DNSZoneProfile"]:
        mo = DNSZoneProfile.objects.filter(id=id)[:1]
        if mo:
            return mo[0]
        else:
            return None

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name):
        mo = DNSZoneProfile.objects.filter(name=name)[:1]
        if mo:
            return mo[0]
        else:
            return None

    def iter_changed_datastream(self, changed_fields=None):
        if not config.datastream.enable_dnszone:
            return
        for z in self.dnszone_set.all():
            for ds, id in z.iter_changed_datastream(changed_fields=changed_fields):
                yield ds, id

    @property
    def authoritative_servers(self):
        """
        Returns a list of DNSServer instances for all zone's master and
        slave servers
        """
        return list(self.masters.all()) + list(self.slaves.all())
