# ---------------------------------------------------------------------
# DNSZone
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import time
import logging
from threading import Lock
from typing import Optional
import operator

# Third-party modules
from django.db import models
from django.contrib.postgres.fields import ArrayField
import cachetools

# NOC modules
from noc.core.model.decorator import on_init
from noc.config import config
from noc.core.model.base import NOCModel
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.systemnotification import SystemNotification
from noc.main.models.label import Label
from noc.project.models.project import Project
from noc.core.ip import IPv6
from noc.core.validators import is_ipv4, is_ipv6
from noc.core.rpsl import rpsl_format
from noc.core.gridvcs.manager import GridVCSField
from noc.core.change.decorator import change
from noc.core.model.decorator import on_delete_check
from noc.core.translation import ugettext as _
from .dnszoneprofile import DNSZoneProfile

logger = logging.getLogger(__name__)
id_lock = Lock()

# Constants
ZONE_FORWARD = "F"
ZONE_REVERSE_IPV4 = "4"
ZONE_REVERSE_IPV6 = "6"


@Label.model
@on_init
@change
@on_delete_check(check=[("dns.DNSZoneRecord", "zone")])
class DNSZone(NOCModel):
    """
    DNS Zone
    """

    class Meta(object):
        verbose_name = _("DNS Zone")
        verbose_name_plural = _("DNS Zones")
        ordering = ["name"]
        db_table = "dns_dnszone"
        app_label = "dns"

    name = models.CharField(_("Domain"), max_length=256, unique=True)
    type = models.CharField(
        _("Type"),
        max_length=1,
        null=False,
        blank=False,
        default=ZONE_FORWARD,
        choices=[
            (ZONE_FORWARD, "Forward"),
            (ZONE_REVERSE_IPV4, "Reverse IPv4"),
            (ZONE_REVERSE_IPV6, "Reverse IPv6"),
        ],
    )
    description = models.CharField(_("Description"), null=True, blank=True, max_length=64)
    project = models.ForeignKey(
        Project,
        verbose_name="Project",
        null=True,
        blank=True,
        related_name="dnszone_set",
        on_delete=models.CASCADE,
    )
    # @todo: Rename to is_provisioned
    is_auto_generated = models.BooleanField(_("Auto generated?"), default=False)
    serial = models.IntegerField(_("Serial"), default=0)
    profile = models.ForeignKey(DNSZoneProfile, verbose_name=_("Profile"), on_delete=models.CASCADE)
    notification_group = models.ForeignKey(
        NotificationGroup,
        verbose_name=_("Notification Group"),
        null=True,
        blank=True,
        help_text=_("Notification group to use when zone changed"),
        on_delete=models.CASCADE,
    )
    paid_till = models.DateField(_("Paid Till"), null=True, blank=True)
    #
    labels = ArrayField(models.CharField(max_length=250), blank=True, null=True, default=list)
    effective_labels = ArrayField(
        models.CharField(max_length=250), blank=True, null=True, default=list
    )

    # Managers
    objects = models.Manager()
    zone = GridVCSField("dnszone")

    # Caches
    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id: int) -> Optional["DNSZone"]:
        zone = DNSZone.objects.filter(id=id)[:1]
        if zone:
            return zone[0]
        return None

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name):
        zone = DNSZone.objects.filter(name=name)[:1]
        if zone:
            return zone[0]
        return None

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_dnszone:
            yield "dnszone", self.id

    def clean(self):
        super().clean()
        self.type = self.get_type_for_zone(self.name or "")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @staticmethod
    def get_type_for_zone(name):
        """
        Zone type. One of:

        * R4 - IPv4 reverse
        * R6 - IPv6 reverse
        * F - forward zone

        :return: Zone type
        :rtype: String
        """
        nl = name.lower()
        if nl.endswith(".in-addr.arpa"):
            return ZONE_REVERSE_IPV4  # IPv4 reverse
        elif nl.endswith(".ip6.int") or nl.endswith(".ip6.arpa"):
            return ZONE_REVERSE_IPV6  # IPv6 reverse
        else:
            return ZONE_FORWARD  # Forward

    rx_rzone = re.compile(r"^(\d+)\.(\d+)\.(\d+)\.in-addr.arpa$")

    @property
    def reverse_prefix(self):
        """
        Appropriative prefix for reverse zone

        :return: IPv4 or IPv6 prefix
        :rtype: String
        """
        if self.type == ZONE_REVERSE_IPV4:
            # Get IPv4 prefix covering reverse zone
            n = self.name.lower()
            if n.endswith(".in-addr.arpa"):
                r = n[:-13].split(".")
                r.reverse()
                length = 4 - len(r)
                r += ["0"] * length
                ml = 32 - 8 * length
                return ".".join(r) + "/%d" % ml
        elif self.type == ZONE_REVERSE_IPV6:
            # Get IPv6 prefix covering reverse zone
            n = self.name.lower()
            if n.endswith(".ip6.int"):
                n = n[:-8]
            elif n.endswith(".ip6.arpa"):
                n = n[:-9]
            else:
                raise Exception("Invalid IPv6 zone suffix")
            p = n.split(".")
            p.reverse()
            length = len(p)
            if length % 4:
                p += ["0"] * (4 - length % 4)
            r = ""
            for i, c in enumerate(p):
                if i and i % 4 == 0:
                    r += ":"
                r += c
            if len(p) != 32:
                r += "::"
            prefix = r + "/%d" % (length * 4)
            return IPv6(prefix).normalized.prefix

    @classmethod
    def get_reverse_for_address(cls, address):
        """
        Return reverse zone holding address
        :param address: Address (as a string)
        :return: DNSZone instance or None
        """
        if ":" in address:
            return cls._get_reverse_for_ipv6_address(address)
        return cls._get_reverse_for_ipv4_address(address)

    @classmethod
    def _get_reverse_for_ipv4_address(cls, address):
        """
        Get reverze zone holding IPv4 address
        :param address: Address (as a string)
        :return: DNSZone instance or None
        """
        parts = list(reversed(address.split(".")))[1:]
        while parts:
            name = "%s.in-addr.arpa" % ".".join(parts)
            zone = DNSZone.get_by_name(name)
            if zone:
                return zone
            parts.pop(0)
        return None

    @classmethod
    def _get_reverse_for_ipv6_address(cls, address):
        """
        Get reverze zone holding IPv6 address
        :param address: Address (as a string)
        :return: DNSZone instance or None
        """
        # @todo: Impelement properly
        parts = [str(x) for x in reversed(IPv6(address).iter_bits())][1:]
        while parts:
            for suffix in (".ip6.int", ".ip6.arpa"):
                name = "%s.%s" % (".".join(parts), suffix)
                zone = DNSZone.get_by_name(name)
                if zone:
                    return zone
            parts.pop(0)  # Remove first par
        return None

    def get_next_serial(self):
        """
        Next zone serial number. Next serial is greater
        than current one. Serial is built using current data
        to follow common practive.

        :return: Zone serial number
        :rtype: int
        """
        T = time.gmtime()
        base = T[0] * 10000 + T[1] * 100 + T[2]
        s_base = self.serial // 100
        if s_base < base:
            return base * 100  # New day
        else:
            return self.serial + 1  # May cause future lap

    def set_next_serial(self):
        old_serial = self.serial
        self.serial = self.get_next_serial()
        logger.info("Zone %s serial change: %s -> %s", self.name, old_serial, self.serial)
        # Hack to not send post_save signal
        DNSZone.objects.filter(id=self.id).update(serial=self.serial)

    @property
    def children(self):
        """List of next-level nested zones"""
        length = len(self.name)
        s = ".%s" % self.name
        return [
            z for z in DNSZone.objects.filter(name__iendswith=s) if "." not in z.name[: -length - 1]
        ]

    @classmethod
    def get_ns_name(cls, ns):
        """Add missed '.' to the end of NS name, if given as FQDN"""
        name = ns.name.strip()
        if not is_ipv4(name) and not name.endswith("."):
            return name + "."
        else:
            return name

    @property
    def ns_list(self):
        """
        Sorted list of zone NSes. NSes are properly formatted and have '.'
        at the end.

        :return: List of zone NSes
        :rtype: List of string
        """
        return sorted(self.get_ns_name(ns) for ns in self.profile.authoritative_servers)

    @property
    def masters(self):
        """
        Sorted list of zone master NSes. NSes are properly formatted and have '.'
        at the end.

        :return: List of zone master NSes
        :rtype: List of string
        :return:
        """
        return sorted(self.get_ns_name(ns) for ns in self.profile.masters.all())

    @property
    def slaves(self):
        """
        Sorted list of zone slave NSes. NSes are properly formatted and have '.'
        at the end.

        :return: List of zone slave NSes
        :rtype: List of string
        :return:
        """
        return sorted(self.get_ns_name(ns) for ns in self.profile.slaves.all())

    @property
    def rpsl(self):
        """
        RPSL for reverse zone. RPSL contains domain: and nserver:
        attributes

        :return: RPSL
        :rtype: String
        """
        if self.type == ZONE_FORWARD:
            return ""
        # Do not generate RPSL for private reverse zones
        if self.name.lower().endswith(".10.in-addr.arpa"):
            return ""
        n1, n2, n = self.name.lower().split(".", 2)
        if "16.172.in-addr.arpa" <= n <= "31.172.in-addr.arpa":
            return ""
        n1, n = self.name.lower().split(".", 1)
        if n == "168.192.in-addr.arpa":
            return ""
        s = ["domain: %s" % self.name] + ["nserver: %s" % ns for ns in self.ns_list]
        return rpsl_format("\n".join(s))

    @classmethod
    def get_zone(cls, name):
        """
        Resolve name to zone object
        :return:
        """

        def get_closest(n):
            """
            Return closest matching zone
            """
            while n:
                try:
                    return DNSZone.objects.get(name=n)
                except DNSZone.DoesNotExist:
                    pass
                n = ".".join(n.split(".")[1:])
            return None

        if not name:
            return None
        if is_ipv4(name):
            # IPv4 zone
            n = name.split(".")
            n.reverse()
            return get_closest("%s.in-addr.arpa" % (".".join(n[1:])))
        elif is_ipv6(name):
            # IPv6 zone
            d = IPv6(name).digits
            d.reverse()
            c = ".".join(d)
            return get_closest("%s.ip6.arpa" % c) or get_closest("%s.ip6.int" % c)
        else:
            return get_closest(name)

    def get_notification_groups(self):
        """
        Get a list of notification groups to notify
        about zone changes
        :return:
        """
        if self.notification_group:
            return [self.notification_group]
        if self.profile.notification_group:
            return [self.profile.notification_group]
        ng = SystemNotification.get_notification_group("dns.change")
        if ng:
            return [ng]
        else:
            return []

    @property
    def is_forward(self):
        return self.type == ZONE_FORWARD

    @property
    def is_reverse_ipv4(self):
        return self.type == ZONE_REVERSE_IPV4

    @property
    def is_reverse_ipv6(self):
        return self.type == ZONE_REVERSE_IPV6

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_dnszone")
