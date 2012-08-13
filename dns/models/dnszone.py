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
from noc.lib.validators import is_ipv4
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
    description = models.CharField(_("Description"), null=True, blank=True,
        max_length=64)
    is_auto_generated = models.BooleanField(_("Auto generated?"))
    serial = models.CharField(_("Serial"),
        max_length=10, default="0000000000")
    profile = models.ForeignKey(DNSZoneProfile, verbose_name=_("Profile"))
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

    ##
    ## Returns a list of zone's RR.
    ## [(left,type,right)]
    ##
    @property
    def records(self):
        """
        All zone records. Zone records returned as list of tuples
        (left, type, right), where type is RR type.

        :return: Zone records
        :trype: List of tuples
        """
        def cmp_ptr(x, y):
            """
            Compare two RR tuples. PTR records are compared as integer,
            other records - as strings.
            """
            x1, x2, x3 = x
            y1, y2, y3 = y
            if "PTR" in x2 and "PTR" in y2:
                try:
                    return cmp(int(x1), int(y1))
                except ValueError:
                    pass
            return cmp(x1, y1)

        def cmp_fwd(x, y):
            """Compare two RR tuples"""
            x1, x2, x3 = x
            y1, y2, y3 = y
            r = cmp(x1, y1)
            if not r:
                r = cmp(x2, y2)
            if not r:
                r = cmp(x3, y3)
            return r

        if self.type == "F":
            # Populate forward zone from IPAM
            records = [
                    (
                        a.fqdn.split(".")[0],
                        "IN  A" if a.afi == "4" else "IN  AAAA",
                        a.address
                    )
                    for a in Address.objects.raw("""
                        SELECT id,address,afi,fqdn
                        FROM   %s
                        WHERE  domainname(fqdn)=%%s
                        ORDER BY address
                        """ % Address._meta.db_table, [self.name])]
            order_by = cmp_fwd
        elif self.type == "R4":
            # Populate IPv4 reverse zone from IPAM
            records = [
                (
                    a.address.split(".")[3],
                    "PTR",
                    a.fqdn + "."
                )
                for a in Address.objects.raw("""
                    SELECT id,address,afi,fqdn
                    FROM %s
                    WHERE
                            address << %%s
                        AND afi='4'
                """ % Address._meta.db_table, [self.reverse_prefix])
                ]
            order_by = cmp_ptr
        elif self.type == "R6":
            # Populate IPv6 reverse zone from IPAM
            origin_length = (len(self.name) - 8 + 1) // 2
            records = [
                (
                    IPv6(a.address).ptr(origin_length),
                    "PTR",
                    a.fqdn + "."
                )
                for a in Address.objects.raw("""
                    SELECT id,address,afi,fqdn
                    FROM %s
                    WHERE
                            address << %%s
                        AND afi='6'
                """ % Address._meta.db_table, [self.reverse_prefix])]
            order_by = cmp_fwd
        else:
            raise Exception("Invalid zone type")
        # Add records from DNSZoneRecord
        zonerecords = self.dnszonerecord_set.all()
        if self.type == "R4":
            # Classles reverse zone delegation
            # Range delegations
            for r in AddressRange.objects.raw("""
                SELECT * FROM
                ip_addressrange
                WHERE
                        from_address<<%s
                    AND to_address<<%s
                    AND action='D'""", [self.reverse_prefix, self.reverse_prefix]):
                nses = [ns.strip() for ns in r.reverse_nses.split(",")]
                for a in r.addresses:
                    n = a.address.split(".")[-1]
                    records += [(n, "CNAME", "%s.%s/32" % (n, n))]
                    for ns in nses:
                        records += [("%s/32" % n, "IN NS", ns)]
            # Subnet delegation macro
            delegations = {}
            for d in [r for r in zonerecords if "NS" in r.type.type and "/" in r.left]:
                r = d.right
                l = d.left
                if l in delegations:
                    delegations[l].append(r)
                else:
                    delegations[l] = [r]
            # Perform classless reverse zone delegation
            for d, nses in delegations.items():
                try:
                    net, mask = [int(x) for x in l.split("/")]
                    if net < 0 or net > 255 or mask <= 24 or mask > 32:
                        raise ValueError("Invalid record")
                except ValueError:
                    records += [(";; Invalid record: %s" % d, "IN NS", "error")]
                    continue
                for ns in nses:
                    records += [(d, "IN NS", str(ns))]
                m = mask - 24
                bitmask = ((1 << m) - 1) << (8 - m)
                if net & bitmask != net:
                    records += [(";; Invalid network: %s" % d, "CNAME", d)]
                    continue
                for i in range(net, net + (1 << (8 - m))):
                    records += [("%d" % i, "CNAME", "%d.%s" % (i, d))]
            # Other records
            records += [(x.left, x.type.type, x.right)
                        for x in zonerecords
                        if ("NS" in x.type.type and "/" not in x.left)
                           or "NS" not in x.type.type]
        else:
            records += [(x.left, x.type.type, x.right) for x in zonerecords]
        # Add NS records if nesessary
        suffix = ".%s." % self.name
        l = len(self.name)
        for z in self.children:
            nested_nses = []
            for ns in z.profile.authoritative_servers:
                ns_name = self.get_ns_name(ns)
                records += [(z.name[:-l - 1], "IN NS", ns_name)]
                # Zone delegated to NS from the child zone
                if ns_name.endswith(suffix) and "." in ns_name[:-len(suffix)]:
                    r = (ns_name[:-len(suffix)], ns.ip)
                    if r not in nested_nses:
                        nested_nses += [r]
            if nested_nses:  # Create A records for nested NSes
                for name, ip in nested_nses:
                    records += [(name, "IN A", ip)]
        # Create missed A records for NSses from zone
        # Find in-zone NSes
        in_zone_nses = {}
        for ns in self.profile.authoritative_servers:
            ns_name = self.get_ns_name(ns)
             # NS server from zone
            if ns_name.endswith(suffix) and "." not in ns_name[:-len(suffix)]:
                in_zone_nses[ns_name[:-len(suffix)]] = ns.ip
        # Find missed in-zone NSes
        for l, t, r in records:
            if l in in_zone_nses and t in ["A", "IN A"]:
                del in_zone_nses[l]
        for name, ip in in_zone_nses.items():
            records += [(name, "IN A", ip)]
        #
        return sorted(records, order_by)

    def zonedata(self, ns):
        """
        Return zone data formatted for given nameserver.

        :param ns: DNS Server
        :type ns: DNSServer instance
        :return: Zone data
        :rtype: String
        """
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
        return [z for z in DNSZone.objects.filter(name__iendswith="." + self.name) if "." not in z.name[:-l - 1]]

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
        return sorted([self.get_ns_name(ns) for ns in self.profile.authoritative_servers])

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
        if n >= "16.172.in-addr.arpa" and n <= "31.172.in-addr.arpa":
            return ""
        n1, n = self.name.lower().split(".", 1)
        if n == "168.192.in-addr.arpa":
            return ""
        s = ["domain: %s" % self.name] + ["nserver: %s" % ns for ns in self.ns_list]
        return rpsl_format("\n".join(s))
