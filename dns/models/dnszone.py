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
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
## NOC modules
from dnszoneprofile import DNSZoneProfile
from noc.main.models import (NotificationGroup, SystemNotification,
                             SystemTemplate)
from noc.project.models.project import Project
from noc.ip.models.address import Address
from noc.ip.models.addressrange import AddressRange
from noc.lib.fields import TagsField
from noc.lib.app.site import site
from noc.lib.ip import IPv6
from noc.lib.validators import is_ipv4, is_ipv6
from noc.lib.rpsl import rpsl_format
from noc.dns.utils.zonefile import ZoneFile
from noc.lib.scheduler.utils import sync_request, sliding_job
from noc.settings import config
from noc.lib.gridvcs.manager import GridVCSField


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
        app_label = "dns"

    name = models.CharField(_("Domain"), max_length=256, unique=True)
    description = models.CharField(_("Description"),
        null=True, blank=True, max_length=64)
    project = models.ForeignKey(
        Project, verbose_name="Project",
        null=True, blank=True, related_name="dnszone_set")
    # @todo: Rename to is_provisioned
    is_auto_generated = models.BooleanField(_("Auto generated?"))
    serial = models.IntegerField(_("Serial"), default=0)
    profile = models.ForeignKey(DNSZoneProfile,
        verbose_name=_("Profile"))
    notification_group = models.ForeignKey(NotificationGroup,
        verbose_name=_("Notification Group"), null=True, blank=True,
        help_text=_("Notification group to use when zone changed"))
    paid_till = models.DateField(_("Paid Till"), null=True, blank=True)
    tags = TagsField(_("Tags"), null=True, blank=True)

    # Managers
    objects = models.Manager()
    forward_zones = ForwardZoneManager()
    reverse_zones = ReverseZoneManager()
    zone = GridVCSField("dnszone")

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
            n = self.name.lower()
            if n.endswith(".in-addr.arpa"):
                r = n[:-13].split(".")
                r.reverse()
                l = 4 - len(r)
                r += ["0"] * l
                ml = 32 - 8 * l
                return ".".join(r) + "/%d" % ml
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
        self.serial = self.next_serial
        # self.save()
        # Hack to not send post_save signal
        DNSZone.objects.filter(id=self.id).update(serial=self.serial)

    @property
    def records(self):
        """
        All zone records. Zone records returned as list of tuples
        (name, type, content), where type is RR type.

        :return: Zone records
        :trype: List of tuples
        """
        # @todo: deprecated
        def f(name, type, content, ttl, prio):
            name = name[:-lnsuffix]  # Strip domain from name
            if type == "CNAME" and content.endswith(nsuffix):
                # Strip domain from content
                content = content[:-lnsuffix]
            if prio is not None:
                content = "%s %s" % (prio, content)

            if prio is not None:
                return name, type, "%s %s" % (prio, content)
            else:
                return name, type, content

        suffix = self.name + "."
        nsuffix = "." + suffix
        lnsuffix = len(nsuffix)
        return [f(a, b, c, d, e)
                for a, b, c, d, e in self.get_records()
                if b != "SOA"]

    def zonedata(self, ns):
        """
        Return zone data formatted for given nameserver.

        :param ns: DNS Server
        :type ns: DNSServer
        :return: Zone data
        :rtype: str
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

    def get_soa(self):
        """
        SOA record
        :return:
        """
        def dotted(s):
            if not s.endswith("."):
                return s + "."
            else:
                return s

        return [(dotted(self.name),
                 "SOA", "%s %s %d %d %d %d %d" % (
            dotted(self.profile.zone_soa),
            dotted(self.profile.zone_contact),
            self.serial,
            self.profile.zone_refresh, self.profile.zone_retry,
            self.profile.zone_expire,
            self.profile.zone_ttl), self.profile.zone_ttl, None)]

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
        def ptr(a):
            """
            Convert address to full PTR record
            """
            x = a.split(".")
            x.reverse()
            return "%s.in-addr.arpa" % (".".join(x))

        ttl = self.profile.zone_ttl
        l = len(self.name) + 1
        return [(
            ptr(a.address)[:-l],
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

    def get_missed_ns_a(self):
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
        ttl = self.profile.zone_ttl
        # Zone NSes
        records = [("", "NS", n, ttl, None) for n in self.ns_list]
        # Add nested NS records if nesessary
        suffix = ".%s." % self.name
        l = len(self.name)
        for z in self.children:
            nested_nses = []
            for ns in z.profile.authoritative_servers:
                ns_name = self.get_ns_name(ns)
                records += [(z.name[:-l - 1], "NS", ns_name,
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
        ttl = self.profile.zone_ttl
        return [
            (r.name, r.type, r.content,
             r.ttl if r.ttl else ttl, r.priority)
            for r in self.dnszonerecord_set.exclude(name__contains="/")
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
            type="NS", name__contains="/")]:
            delegations[d.name] += [d.content]
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
        def cmp_fwd(x, y):
            sn = self.name + "."
            return cmp(
                (None if x[0] == sn else x[0], x[1], x[2], x[3], x[4]),
                (None if y[0] == sn else y[0], y[1], y[2], y[3], y[4])
            )

        def cmp_ptr(x, y):
            """
            Compare two RR tuples. PTR records are compared as integer,
            other records - as strings.
            """
            x1, x2, _, _, _ = x
            y1, y2, _, _, _ = y
            if x2 == "NS" and y2 != "NS":
                return -1
            if x2 != "NS" and y2 == "NS":
                return 1
            if x2 == y2 == "PTR":
                try:
                    return cmp(int(x1), int(y1))
                except ValueError:
                    pass
            return cmp(x, y)

        def fr(r):
            name, type, content, ttl, prio = r
            if not name.endswith("."):
                if name:
                    name += ".%s." % self.name
                else:
                    name = self.name + "."
            if (type in ("NS", "MX", "CNAME") and
                not content.endswith(".")):
                if content:
                    content += ".%s." % self.name
                else:
                    content = self.name + "."
            return name, type, content, ttl, prio

        records = []
        records += self.get_rr()
        records += self.get_ns()
        if self.type == "F":
            records += self.get_ipam_a()
            records += self.get_missed_ns_a()
            order_by = cmp_fwd
        elif self.type == "R4":
            records += self.get_ipam_ptr4()
            records += self.get_classless_delegation()
            order_by = cmp_ptr
        elif self.type == "R6":
            records += self.get_ipam_ptr6()
            order_by = cmp_ptr
        else:
            raise ValueError("Invalid zone type")
        records = (self.get_soa() +
                   sorted(set(fr(r) for r in records), order_by))
        return records

    def get_zone_text(self):
        """
        BIND-style zone text for configuration management
        :return:
        """
        zf = ZoneFile(zone=self.name, records=self.get_records())
        return zf.get_text()

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
            return (get_closest("%s.ip6.arpa" % c) or
                    get_closest("%s.ip6.int" % c))
        else:
            return get_closest(name)

    @classmethod
    def touch(cls, name):
        """
        Mark zone as dirty
        :param cls:
        :param name:
        :return:
        """
        z = cls.get_zone(name)
        if z and z.is_auto_generated:
            z._touch()

    def _touch(self, is_new=False):
        if self.is_auto_generated:
            sliding_job("main.jobs", "dns.touch_zone", key=self.id,
                delta=config.getint("dns", "delay"),
                cutoff_delta=config.getint("dns", "cutoff"),
                data={"new": is_new}
            )

    @property
    def channels(self):
        return sorted(
            set("dns/zone/%s" % c for c in
                self.profile.masters.filter(sync_channel__isnull=False)
                .values_list("sync_channel", flat=True)))

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

    def refresh_zone(self):
        """
        Compare zone state with stored one.
        Increase serial and store new version on change
        :return: True if zone has been changed
        """
        # Stored version
        cz = self.zone.read()
        # Generated version
        nz = self.get_zone_text()
        if cz == nz:
            return False  # Not changed
         # Step serial
        self.set_next_serial()
        # Generate new zone again
        # Because serial has been changed
        zt = self.get_zone_text()
        self.zone.write(zt)
        # Set change notifications
        groups = self.get_notification_groups()
        if groups:
            ctx = {"name": self.name}
            if cz:
                revs = self.zone.get_revisions()[-2:]
                stpl = "dns.zone.change"
                ctx["diff"] = self.zone.diff(revs[0], revs[1])
            else:
                stpl = "dns.zone.new"
                ctx["data"] = zt
            try:
                t = SystemTemplate.objects.get(name=stpl)
            except SystemTemplate.DoesNotExist:
                return True
            subject = t.render_subject(**ctx)
            body = t.render_body(**ctx)
            for g in groups:
                g.notify(subject, body)
        return True


##
## Signal handlers
##
@receiver(post_save, sender=DNSZone)
def on_save(sender, instance, created, **kwargs):
    if instance.is_auto_generated and not hasattr(instance, "_nosignal"):
        instance._touch(is_new=created)


@receiver(pre_delete, sender=DNSZone)
def on_delete(sender, instance, **kwargs):
    sync_request(instance.channels, "list", delta=5)
    # @todo: Delete from repo
