# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DNSZone
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
import time
from collections import defaultdict
# Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models import Q
## NOC modules
from dnszoneprofile import DNSZoneProfile
from noc.main.models import NotificationGroup
from noc.ip.models import Address, AddressRange
from noc.lib.fields import AutoCompleteTagsField
from noc.lib.app.site import site
from noc.lib.ip import IPv6
from noc.lib.validators import is_ipv4, is_int
from noc.lib.rpsl import rpsl_format


##
## Managers for DNSZone
##
class ForwardZoneManager(models.Manager):
    def get_query_set(self):
        q = (Q(name__iendswith=".in-addr.arpa") |
             Q(name__iendswith=".ip6.int") |
             Q(name__iendswith=".ip6.arpa"))
        return super(ForwardZoneManager, self).get_query_set().exclude(q)


class ReverseZoneManager(models.Manager):
    def get_query_set(self):
        q = (Q(name__iendswith=".in-addr.arpa") |
             Q(name__iendswith=".ip6.int") |
             Q(name__iendswith=".ip6.arpa"))
        return super(ReverseZoneManager, self).get_query_set().filter(q)


class DNSZone(models.Model):
    """
    DNS Zone
    """
    class Meta:
        verbose_name = _("DNS Zone")
        verbose_name_plural = _("DNS Zones")
        ordering = ["name"]
        db_table = "dns_dnszone"

    name = models.CharField(_("Domain"), max_length=256, unique=True)
    description = models.CharField(_("Description"),
        null=True, blank=True, max_length=64)
    is_auto_generated = models.BooleanField(_("Auto generated?"))
    serial = models.CharField(_("Serial"),
        max_length=10, default="0000000000")
    profile = models.ForeignKey(DNSZoneProfile,
        verbose_name=_("Profile"))
    notification_group = models.ForeignKey(NotificationGroup,
        verbose_name=_("Notification Group"), null=True, blank=True,
        help_text=_("Notification group to use when zone changed"))
    paid_till = models.DateField(_("Paid Till"), null=True, blank=True)
    tags = AutoCompleteTagsField(_("Tags"), null=True, blank=True)

    # Managers
    objects = models.Manager()
    forward_zones = ForwardZoneManager()
    reverse_zones = ReverseZoneManager()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        """Return link to zone preview

        :return: URL
        :rtype: String
        """
        return site.reverse("dns:dnszone:change", self.id)

    @property
    def type(self):
        """
        Zone type. One of:

        * R4 - IPv4 reverse
        * R6 - IPv6 reverse
        * F - forward zone

        :return: Zone type
        :rtype: String
        """
        nl = self.name.lower()
        if nl.endswith(".in-addr.arpa"):
            return "R4"  # IPv4 reverse
        elif nl.endswith(".ip6.int") or nl.endswith(".ip6.arpa"):
            return "R6"  # IPv6 reverse
        else:
            return "F"  # Forward

    rx_rzone = re.compile(r"^(\d+)\.(\d+)\.(\d+)\.in-addr.arpa$")

    @property
    def reverse_prefix(self):
        """
        Appropriative prefix for reverse zone

        :return: IPv4 or IPv6 prefix
        :rtype: String
        """
        if self.type == "R4":
            # Get IPv4 prefix covering reverse zone
            match = self.rx_rzone.match(self.name.lower())
            if match:
                return "%s.%s.%s.0/24" % (match.group(3), match.group(2),
                                          match.group(1))
        elif self.type == "R6":
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
            l = len(p)
            if l % 4:
                p += [u"0"] * (4 - l % 4)
            r = ""
            for i, c in enumerate(p):
                if i and i % 4 == 0:
                    r += ":"
                r += c
            if len(p) != 32:
                r += "::"
            prefix = r + "/%d" % (l * 4)
            return IPv6(prefix).normalized.prefix

    @property
    def next_serial(self):
        """
        Next zone serial number. Next serial is greater
        than current one. Serial is built using current data
        to follow common practive.

        :return: Zone serial number
        :rtype: String
        """
        T = time.gmtime()
        p = "%04d%02d%02d" % (T[0], T[1], T[2])
        sn = int(self.serial[-2:])
        if self.serial.startswith(p):
            return p + "%02d" % (sn + 1)
        return p + "00"

    @property
    def records(self):
        """
        All zone records. Zone records returned as list of tuples
        (left, type, right), where type is RR type.

        :return: Zone records
        :trype: List of tuples
        """
        # @todo: deprecated
        def f(name, type, content, ttl, prio):
            if prio is not None:
                return name, type, "%s %s" % (prio, content)
            else:
                return name, type, content

        return [f(a, b, c, d, e)
                for a, b, c, d, e in self.get_records()]

    def zonedata(self, ns):
        """
        Return zone data formatted for given nameserver.

        :param ns: DNS Server
        :type ns: DNSServer instance
        :return: Zone data
        :rtype: String
        """
        # @todo: deprecated
        return ns.generator_class().get_zone(self)

    @property
    def distribution_list(self):
        """List of DNSServers to distribute zone

        :return: List of DNSServers
        :rtype: List of DNSServer instances
        """
        return self.profile.masters.filter(provisioning__isnull=False)

    @property
    def children(self):
        """List of next-level nested zones"""
        l = len(self.name)
        s = ".%s" % self.name
        return [z for z in DNSZone.objects.filter(name__iendswith=s)
                if "." not in z.name[:-l - 1]]

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
        return sorted(self.get_ns_name(ns)
            for ns in self.profile.authoritative_servers)

    @property
    def rpsl(self):
        """
        RPSL for reverse zone. RPSL contains domain: and nserver:
        attributes

        :return: RPSL
        :rtype: String
        """
        if self.type == "F":
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
        s = ["domain: %s" % self.name] + ["nserver: %s" % ns
                                          for ns in self.ns_list]
        return rpsl_format("\n".join(s))

    def get_ipam_a(self):
        """
        Fetch A/AAAA records from IPAM
        :return: (name, type, content, ttl, prio)
        """
        ttl = self.profile.zone_ttl
        return [(
            a.fqdn.split(".")[0],
            "A" if a.afi == "4" else "AAAA",
            a.address,
            ttl,
            None
            ) for a in Address.objects.extra(
                where=["domainname(fqdn)=%s"], params=[self.name])
        ]

    def get_ipam_ptr4(self):
        """
        Fetch IPv4 PTR records from IPAM
        :return: (name, type, content, ttl, prio)
        """
        ttl = self.profile.zone_ttl
        return [(
            a.address.split(".")[3],
            "PTR",
            a.fqdn + ".",
            ttl,
            None
            ) for a in Address.objects.filter(afi="4").extra(
                where=["address << %s"], params=[self.reverse_prefix])
        ]

    def get_ipam_ptr6(self):
        """
        Fetch IPv6 PTR records from IPAM
        :return: (name, type, content, ttl, prio)
        :return:
        """
        ttl = self.profile.zone_ttl
        origin_length = (len(self.name) - 8 + 1) // 2
        return [(
            IPv6(a.address).ptr(origin_length),
            "PTR",
            a.fqdn + ".",
            ttl,
            None
            ) for a in Address.objects.filter(afi="6").extra(
            where=["address << %s"], params=[self.reverse_prefix])
        ]

    def get_missed_ns_a(self, records):
        """
        Returns missed A record for NS'es
        :param records:
        :return:
        """
        suffix = ".%s." % self.name
        ttl = self.profile.zone_ttl
        # Create missed A records for NSses from zone
        # Find in-zone NSes
        in_zone_nses = {}
        for ns in self.profile.authoritative_servers:
            if not ns.ip:
                continue
            ns_name = self.get_ns_name(ns)
             # NS server from zone
            if (ns_name.endswith(suffix) and
                "." not in ns_name[:-len(suffix)]):
                in_zone_nses[ns_name[:-len(suffix)]] = ns.ip
        # Find missed in-zone NSes
        return [(name, "A", in_zone_nses[name], ttl, None)
            for name in in_zone_nses
            if not (name in in_zone_nses and type in ("A", "IN A"))]

    def get_ns(self):
        # Add NS records if nesessary
        records = []
        suffix = ".%s." % self.name
        ttl = self.profile.zone_ttl
        l = len(self.name)
        for z in self.children:
            nested_nses = []
            for ns in z.profile.authoritative_servers:
                ns_name = self.get_ns_name(ns)
                records += [(z.name[:-l - 1], "IN NS", ns_name,
                             ttl, None)]
                # Zone delegated to NS from the child zone
                if (ns_name.endswith(suffix) and
                    "." in ns_name[:-len(suffix)]):
                    r = (ns_name[:-len(suffix)], ns.ip)
                    if r not in nested_nses:
                        nested_nses += [r]
            if nested_nses:  # Create A records for nested NSes
                for name, ip in nested_nses:
                    records += [(name, "A", ip, ttl, None)]
        return records

    def get_rr(self):
        """
        Get RRs from database
        :return:
        """
        def f(name, type, content, ttl, prio):
            """
            Process MX record priority
            """
            if type == "MX":
                if " " in content:
                    p, rest = content.split(" ", 1)
                    if is_int(p):
                        return name, type, rest, ttl, int(p)
            return name, type, content, ttl, prio

        ttl = self.profile.zone_ttl
        return [f(r.left, r.type.type, r.right, ttl, None)
            for r in self.dnszonerecord_set.exclude(left__contains="/")
        ]

    def get_classless_delegation(self):
        """
        Classless reverse zone delegation
        :return:
        """
        records = []
        ttl = self.profile.zone_ttl
        # Range delegations
        for r in AddressRange.objects.filter(action="D").extra(
            where=["from_address << %s", "to_address << %s"],
            params=[self.reverse_prefix, self.reverse_prefix]):
            nses = [ns.strip() for ns in r.reverse_nses.split(",")]
            for a in r.addresses:
                n = a.address.split(".")[-1]
                records += [(n, "CNAME", "%s.%s/32" % (n, n), ttl, None)]
                for ns in nses:
                    if not ns.endswith("."):
                        ns += "."
                    records += [("%s/32" % n, "NS", ns, ttl, None)]
        # Subnet delegation macro
        delegations = defaultdict(list)
        for d in [r for r in self.dnszonerecord_set.filter(
            type__type__contains="NS", left__contains="/")]:
            delegations[d.left] += [d.right]
        # Perform classless reverse zone delegation
        for d in delegations:
            nses = delegations[d]
            net, mask = [int(x) for x in d.split("/")]
            if net < 0 or net > 255 or mask <= 24 or mask > 32:
                continue  # Invalid record
            for ns in nses:
                ns = str(ns)
                if not ns.endswith("."):
                    ns += "."
                records += [(d, "NS", ns, ttl, None)]
            m = mask - 24
            bitmask = ((1 << m) - 1) << (8 - m)
            if net & bitmask != net:
                continue  # Invalid network
            records += [(str(i), "CNAME", "%d.%s" % (i, d), ttl, None)
                for i in range(net, net + (1 << (8 - m)))
            ]
        return records

    def get_records(self):
        def cmp_ptr(x, y):
            """
            Compare two RR tuples. PTR records are compared as integer,
            other records - as strings.
            """
            x1, x2, _, _, _ = x
            y1, y2, _, _, _ = y
            if x2 == y2 == "PTR":
                try:
                    return cmp(int(x1), int(y1))
                except ValueError:
                    pass
            return cmp(x, y)

        records = []
        records += self.get_rr()
        records += self.get_ns()
        if self.type == "F":
            records += self.get_ipam_a()
            records += self.get_missed_ns_a(records)
            order_by = cmp
        elif self.type == "R4":
            records += self.get_ipam_ptr4()
            records += self.get_classless_delegation()
            order_by = cmp_ptr
        elif self.type == "R6":
            records += self.get_ipam_ptr6()
            order_by = cmp_ptr
        else:
            raise ValueError("Invalid zone type")
        return sorted(records, order_by)
