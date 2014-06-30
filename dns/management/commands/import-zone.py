# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Import DNS Zone
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
from optparse import make_option
import logging
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.dns.models.dnszone import DNSZone
from noc.dns.models.dnszonerecord import DNSZoneRecord
from noc.dns.models.dnszoneprofile import DNSZoneProfile
from noc.ip.models.vrf import VRF
from noc.ip.models.address import Address
from noc.lib.debug import error_report
from noc.lib.validators import is_int


class Command(BaseCommand):
    help = "Import DNS zone"

    option_list = BaseCommand.option_list + (
        make_option("-t", "--test",
            action="store_true", dest="test",
            help="Test only. Do not save records"),

        make_option("-c", "--clean",
            action="store_true", dest="clean",
            help="Clean up zone before store"),

        make_option("-p", "--profile",
            action="store", dest="profile",
            help="Set Zone Profile"),

    )

    RR_TYPES = [
        "A",
        "AAAA",
        "AFSDB",
        "AXFR",
        "CERT",
        "CNAME",
        "DHCID",
        "DLV",
        "DNAME",
        "DNSKEY",
        "DS",
        "HIP",
        "IPSECKEY",
        "IXFR",
        "KEY",
        "LOC",
        "MX",
        "NAPTR",
        "NS",
        "NSEC",
        "NSEC3",
        "NSEC3PARAM",
        "OPT",
        "PTR",
        "RRSIG",
        "SIG",
        "SPF",
        "SRV",
        "SSHFP",
        "TA",
        "TKEY",
        "TSIG",
        "TXT"
    ]

    def handle(self, *args, **options):
        # Sync
        try:
            for path in args:
                self.import_zone(path, options)
        except CommandError, why:
            raise
        except:
            error_report()

    def info(self, msg, *args):
        if args:
            print msg % tuple(args)
        else:
            print msg

    def get_profile(self, options):
        """
        Get DNSZone profile from --profile option
        """
        profile = options["profile"]
        if not profile:
            raise CommandError("--profile option is missed")
        try:
            return DNSZoneProfile.objects.get(name=profile)
        except DNSZoneProfile.DoesNotExist:
            raise CommandError("DNS zone profile '%s' not found" % profile)

    def import_zone(self, path, options):
        is_test = bool(options["test"])
        self.info("Loading zone file '%s'" % path)
        with open(path) as f:
            data = f.read()
        self.info("Parsing zone file using BIND parser")
        zone, rrs = self.parse_bind_zone(data)
        if not zone or not rrs:
            raise CommandError("Unable to parse zone file")
        # Find profile
        profile = self.get_profile(options)
        # Get or create zone
        to_clean = bool(options["clean"])
        try:
            z = DNSZone.objects.get(name=zone)
            self.info("Using existing zone '%s'" % z)
        except DNSZone.DoesNotExist:
            self.info("Creating zone '%s'" % zone)
            z = DNSZone(name=zone, profile=profile)
            to_clean = False  # Nothing to clean yet
        if z.profile != profile:
            self.info("Setting profile to '%s'" % profile)
            z.profile = profile
        if not is_test:
            z.save()
        # Clean zone when necessary
        if to_clean and z.id:
            self.info("Cleaning zone")
            for rr in z.dnszonerecord_set.all():
                self.info("Removing %s %s" % (rr.type, rr.name))
                if not is_test:
                    rr.delete()
        # Populate zone
        vrf = VRF.get_global()
        zz = zone + "."
        lz = len(zz)
        if zone.endswith(".in-addr.arpa"):
            # Calculate prefix for reverse zone
            zp = zone[:-13].split(".")
            zp.reverse()
            zp = ".".join(zp) + "."
        else:
            # @todo: IPv6 reverse
            zp = None
        for name, t, value, ttl, priority in rrs:
            # print name, t, value
            if name.endswith(zz):
                name = name[:-lz]
            if name.endswith("."):
                name = name[:-1]
            rr = None
            if (t == "SOA") or (t == "NS" and not name):
                continue
            if t in ("A", "AAAA"):
                afi = "4" if t == "A" else "6"
                self.create_address(
                    zone, vrf, afi, value,
                    "%s.%s" % (name, zone) if name else zone, is_test)
            elif t == "PTR":
                if not zp:
                    raise CommandError("IPv6 reverse zone import is still not supported")
                address = zp + name
                afi = "6" if ":" in address else "4"
                self.create_address(zone, vrf, afi, address, value, is_test)
            else:
                rr = DNSZoneRecord(
                    zone=z, name=name, type=t,
                    ttl=ttl, priority=priority
                )
            if rr:
                self.info("Creating %s %s" % (rr.type, rr.name))
                if not is_test:
                    rr.save()

    def create_address(self, zone, vrf, afi, address, fqdn, is_test):
        """
        Create IPAM record
        """
        try:
            a = Address.objects.get(
                vrf=vrf,
                afi=afi,
                address=address
            )
            self.info("Address %s (%s) is already exists in IPAM, ignoring" % (a.address, a.fqdn))
        except Address.DoesNotExist:
            a = Address(
                vrf=vrf,
                afi=afi,
                address=address,
                fqdn=fqdn,
                description="Imported from %s zone" % zone
            )
            self.info("Creating address %s (%s)" % (a.address, a.fqdn))
            if not is_test:
                a.save()

    def strip_oneline_comments(self, data, csym=";"):
        """
        Strip one-line comments from *csym* to end of line
        """
        def nq(s, q="\""):
            return sum(1 for c in s if c == q)

        r = []
        for l in data.splitlines():
            if csym in l:
                # Detect csym is not within string
                i = -1
                while True:
                    i = l.find(csym, i + 1)
                    if i == -1:
                        break
                    if nq(l[:i]) % 2 == 0:
                        # Strip comment
                        l = l[:i - 1] if i else ""
                        break
            r += [l.strip()]
        return "\n".join(l for l in r if l)

    def merge_enclosed(self, data):
        """
        Merge lines enclosed by ( ... )
        """
        r = []
        to_append = False
        for l in data.splitlines():
            if to_append:
                r[-1] += " " + l
                if l.endswith(")"):
                    to_append = False
            else:
                r += [l]
                if l.endswith("("):
                    to_append = True
        return "\n".join(r)

    rx_soa = re.compile(
        r"^(?P<zone>\S+)\s+(?:IN\s+)?SOA\s+(\S+)\s+(\S+)\s*\(\s*"
        r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*\)$"
    )
    def parse_bind_zone(self, data):
        """
        Parse bind-style zone and return records applicable to
        ZoneFile
        (fqdn, type, content, ttl, prio)
        """
        # Wipe out comments
        data = data.replace("\t", "        ")
        data = self.strip_oneline_comments(data, ";")
        data = self.merge_enclosed(data)
        ttl = None
        zone = None
        rr = []
        for l in data.splitlines():
            if l.startswith("$TTL "):
                ttl = int(l[5:].strip())
                continue
            if l.startswith("$ORIGIN "):
                zone = l[8:].strip()
                continue
            if not rr:
                # Wait for SOA
                match = self.rx_soa.match(l)
                if match:
                    z = match.group("zone")
                    if z and z != "@":
                        zone = z
                    rr += [["", "SOA", " ".join(match.groups()[-7:]), None, None]]
            else:
                parts = l.split()
                if parts[0] == "IN" or parts[0] in self.RR_TYPES:
                    # missed name
                    parts = [""] + parts
                if parts[1] == "IN":
                    # Remove IN
                    parts = [parts[0]] + parts[2:]
                # Normalize name
                name = parts[0]
                if name == "@" or not name:
                    name = zone
                elif not name.endswith("."):
                    name = name + "." + zone
                # Process value
                t = parts[1]
                v = parts[2:]
                rttl = None
                if len(v) > 1 and is_int(v[0]):
                    rprio = int(v[0])
                    v = v[1:]
                else:
                    rprio = None
                value = " ".join(v)
                if t in ("CNAME", "PTR"):
                    value = self.from_idna(value)
                rr += [[self.from_idna(name), t, value, rttl, rprio]]
        if zone.endswith("."):
            zone = zone[:-1]
        return self.from_idna(zone), rr

    def from_idna(self, s):
        """
        Convert IDNA domain name to unicode
        """
        if not s:
            return
        return ".".join(unicode(x, "idna") for x in s.split("."))
