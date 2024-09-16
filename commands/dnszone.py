# ---------------------------------------------------------------------
# Import DNS Zone
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import dns
import argparse
import re
from itertools import zip_longest

# NOC modules
from noc.core.management.base import BaseCommand, CommandError
from noc.core.mongo.connection import connect
from noc.dns.models.dnszone import DNSZone
from noc.dns.models.dnszonerecord import DNSZoneRecord
from noc.dns.models.dnszoneprofile import DNSZoneProfile
from noc.ip.models.vrf import VRF
from noc.ip.models.addressprofile import AddressProfile
from noc.ip.models.address import Address
from noc.core.validators import is_int, is_ipv4, is_ipv6
from noc.core.dns.rr import RR
from noc.core.text import split_alnum
from noc.core.comp import smart_text


class Command(BaseCommand):
    help = "DNS zone manipulation tool"
    # Time multipliers
    TIMES = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        #
        import_parser = subparsers.add_parser("import")
        import_parser.add_argument(
            "--dry-run", dest="dry_run", action="store_true", help="Test only. Do not save records"
        ),
        import_parser.add_argument(
            "-c", "--clean", dest="clean", action="store_true", help="Clean up zone before store"
        ),
        import_parser.add_argument(
            "--zone-profile", dest="zone_profile", action="store", help="Set Zone Profile"
        ),
        import_parser.add_argument(
            "--address-profile", dest="address_profile", action="store", help="Set Address Profile"
        ),
        import_parser.add_argument(
            "-f",
            "--force",
            dest="force",
            action="store_true",
            help="Forcefully update FQDN for A records",
        ),
        import_parser.add_argument("paths", nargs=argparse.REMAINDER, help="Path to zone files")
        import_parser.add_argument(
            "--axfr",
            action="store_true",
            help="Upload list of allocated IP addresses from existing DNS servers via AXFR request",
        )
        import_parser.add_argument(
            "--nameserver",
            dest="nameserver",
            action="store",
            help="Name server IP address. NS must have zone transfer enabled for NOC host",
        ),
        import_parser.add_argument(
            "--transfer-zone",
            dest="transfer_zone",
            action="store",
            help="DNS Zone name to transfer",
        )
        self.print((import_parser.print_help()))

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
        "TXT",
    ]

    def handle(self, cmd, *args, **options):
        connect()
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_import(
        self,
        paths,
        axfr=False,
        force=False,
        clean=False,
        dry_run=False,
        zone_profile=None,
        address_profile=None,
        transfer_zone=None,
        nameserver=None,
    ):
        if not axfr and not zone_profile:
            self.die("--zone-profile is not set")
        if not address_profile:
            self.die("--address-profile is not set")
        zp = DNSZoneProfile.get_by_name(zone_profile)
        if not axfr and not zp:
            self.die("Invalid zone profile '%s'" % zone_profile)
        ap = AddressProfile.get_by_name(address_profile)
        if not ap:
            self.die("Invalid address profile '%s'" % address_profile)
        if paths:
            for path in paths:
                self.import_zone(
                    path=path,
                    force=force,
                    clean=clean,
                    dry_run=dry_run,
                    zone_profile=zp,
                    address_profile=ap,
                )
        if axfr:
            if not transfer_zone:
                self.die("--transfer_zone is not set")
            if not nameserver:
                self.die("--nameserver is not set")
            self.import_zone(
                axfr=axfr,
                force=force,
                clean=clean,
                dry_run=dry_run,
                zone_profile=zp,
                address_profile=ap,
                transfer_zone=transfer_zone,
                nameserver=nameserver,
            )

    def load_axfr(self, ip, transfer_zone):
        try:
            _zone = dns.zone.from_xfr(
                dns.query.xfr(str(ip).rstrip("."), transfer_zone, lifetime=5.0)
            )
            data = "\n".join(
                _zone[z_node].to_text(z_node)
                for z_node in _zone.nodes.keys()
                if "@" not in _zone[z_node].to_text(z_node)
            )
        except dns.exception.DNSException as e:
            self.print("ERROR:", e)
            return
        return data

    def dns_zone(self, zone, zone_profile, dry_run=False, clean=False):
        z = DNSZone.get_by_name(zone)
        if z:
            self.print("Using existing zone '%s'" % zone)
        else:
            self.print("Creating zone '%s'" % zone)
            z = DNSZone(name=zone, profile=zone_profile)
            clean = False  # Nothing to clean
        if z.profile.id != zone_profile.id:
            self.print("Setting profile to '%s'" % zone_profile.name)
            z.profile = zone_profile
        # Apply changes
        if dry_run:
            z.clean()  # Set type
        else:
            z.save()
        #  Clean zone when necessary
        if clean:
            self.print("Cleaning zone")
            for rr in DNSZoneRecord.objects.filter(zone=z):
                self.print("Removing %s %s" % (rr.type, rr.name))
                if not dry_run:
                    rr.delete()
        return z

    def import_zone(
        self,
        path=None,
        axfr=False,
        zone_profile=None,
        address_profile=None,
        transfer_zone=None,
        nameserver=None,
        dry_run=False,
        force=False,
        clean=False,
    ):
        if path:
            self.print("Loading zone file '%s'" % path)
            self.print("Parsing zone file using BIND parser")
            with open(path) as f:
                rrs = self.iter_bind_zone_rr(f)
                try:
                    soa = next(rrs)
                except StopIteration:
                    raise CommandError("Unable to parse zone file from %s" % path)
                zone = self.from_idna(soa.zone)
                z = self.dns_zone(zone, zone_profile, dry_run, clean)
                # Populate zone
                vrf = VRF.get_global()
                zz = zone + "."
                lz = len(zz)
                if z.is_forward:
                    zp = None
                elif z.is_reverse_ipv4:
                    # Calculate prefix for reverse zone
                    zp = ".".join(reversed(zone[:-13].split("."))) + "."
                elif z.is_reverse_ipv6:
                    raise CommandError("IPv6 reverse import is not implemented")
                else:
                    raise CommandError("Unknown zone type")
                for rr in rrs:
                    name = rr.name
                    if name.endswith(zz):
                        name = name[:-lz]
                    if name.endswith("."):
                        name = name[:-1]
                    # rr = None
                    # Skip zone NS
                    if rr.type == "NS" and not name:
                        continue
                    if rr.type in ("A", "AAAA"):
                        self.create_address(
                            zone,
                            vrf,
                            rr.rdata,
                            "%s.%s" % (name, zone) if name else zone,
                            address_profile,
                            dry_run=dry_run,
                            force=force,
                        )
                    elif rr.type == "PTR":
                        if "." in name:
                            address = zp + ".".join(reversed(name.split(".")))
                        else:
                            address = zp + name
                        self.create_address(
                            zone,
                            vrf,
                            address,
                            rr.rdata,
                            address_profile,
                            dry_run=dry_run,
                            force=force,
                        )
                    else:
                        zrr = DNSZoneRecord(
                            zone=z,
                            name=name,
                            type=rr.type,
                            ttl=rr.ttl,
                            priority=rr.priority,
                            content=rr.rdata,
                        )
                        self.print("Creating %s %s" % (rr.type, rr.name))
                        if not dry_run:
                            zrr.save()
        if axfr:
            self.print("Loading zone: %s by AXFR from server: %s" % (transfer_zone, nameserver))
            if not is_ipv4(nameserver) and not is_ipv6(nameserver):
                try:
                    answer = dns.resolver.resolve(qname=nameserver, rdtype="A", lifetime=5.0)
                    ip = answer[0].address
                except dns.exception.DNSException as e:
                    self.print(f"Resolv Error: {e}")
                    return
            else:
                ip = nameserver
            print(ip, transfer_zone)
            data = self.load_axfr(ip, transfer_zone)
            if data is None:
                self.print("No result")
                return
            zone = self.from_idna(transfer_zone)
            z = self.dns_zone(zone, zone_profile, dry_run, clean)
            # Populate zone
            vrf = VRF.get_global()
            if not z.is_forward and not z.is_reverse_ipv4 and not z.is_reverse_ipv6:
                raise CommandError("Unknown zone type")
            for row in data.splitlines():
                row = row.strip().split()
                if len(row) != 5 or row[3] not in ("A", "AAAA", "PTR"):
                    continue
                if row[3] == "PTR":
                    host = dns.name.from_text(f"{row[0]}.{zone}.")
                    ip = dns.reversename.to_address(host)
                    fqdn = row[4]
                    if fqdn.endswith("."):
                        fqdn = fqdn[:-1]
                elif row[3] in ("A", "AAAA"):
                    fqdn = row[0]
                    if fqdn.endswith(zz):
                        fqdn = fqdn[:-lz]
                    if fqdn.endswith("."):
                        fqdn = fqdn[:-1]
                    ip = row[4]
                else:
                    continue
                self.create_address(
                    zone,
                    vrf,
                    ip,
                    fqdn,
                    address_profile,
                    dry_run=dry_run,
                    force=force,
                )

    def create_address(self, zone, vrf, address, fqdn, address_profile, dry_run=False, force=False):
        """
        Create IPAM record
        """
        afi = "6" if ":" in address else "4"
        a = Address.objects.filter(vrf=vrf, afi=afi, address=address).first()
        if a:
            if force:
                if a.fqdn != fqdn:
                    self.print("Updating FQDN %s (%s)" % (a.address, a.fqdn))
                    a.fqdn = fqdn
                    a.name = fqdn
                    if not dry_run:
                        a.save()
            else:
                self.print(
                    "Address %s (%s) is already exists in IPAM, ignoring" % (a.address, a.fqdn)
                )
        else:
            # Not found
            a = Address(
                vrf=vrf,
                afi=afi,
                address=address,
                profile=address_profile,
                fqdn=fqdn,
                name=fqdn,
                description="Imported from %s zone" % zone,
            )
            self.print("Creating address %s (%s)" % (a.address, a.fqdn))
            if not dry_run:
                a.save()

    rx_q = re.compile('("[^"]*")')

    @classmethod
    def iter_tokenize(cls, s):
        start = 0
        for match in cls.rx_q.finditer(s):
            if start < match.start():
                yield s[start : match.start()]
            yield match.group(0)
            start = match.end()
        if start < len(s) - 1:
            yield s[start:]

    @classmethod
    def iter_tabify(cls, iter):
        """
        Replace tabs to spaces in non-quoted parts
        :param iter:
        :return:
        """
        for item in iter:
            if cls.has_unquoted(item, "\t"):
                yield item.replace("\t", "        ")
            else:
                yield item

    @classmethod
    def iter_strip_comments(cls, iter):
        """
        Cut comments to end of line
        :param iter:
        :return:
        """
        for item in iter:
            if cls.has_unquoted(item, ";"):
                p = item.split(";", 1)[0].rstrip()
                if p:
                    yield p
                break
            else:
                yield item

    @staticmethod
    def is_quoted(item):
        return item.startswith('"')

    @staticmethod
    def has_unquoted(item, v):
        return not item.startswith('"') and v in item

    rx_mq = re.compile(r'"\s+"')

    @classmethod
    def merge_mq(cls, value):
        return cls.rx_mq.sub("", value)

    @classmethod
    def iter_zone_lines(cls, f):
        """
        Yields zone data line by line
        :param f: File object
        :return:
        """
        enclosed_line = []
        for line in f:
            collected = []
            for item in cls.iter_strip_comments(cls.iter_tabify(cls.iter_tokenize(line))):
                if enclosed_line:
                    if cls.has_unquoted(item, ")"):
                        # Closing )
                        p = item.split(")", 1)
                        enclosed_line += [p[0] + " "]
                        if len(p) > 1:
                            enclosed_line += [p[1] + " "]
                        collected += enclosed_line
                        enclosed_line = []
                    else:
                        enclosed_line += [item]
                elif cls.has_unquoted(item, "("):
                    # Starting (
                    p = item.split("(", 1)
                    enclosed_line += [p[0] + " "]
                    if len(p) > 1:
                        enclosed_line += [p[1] + " "]
                else:
                    # Plain item
                    collected += [item]
            if collected and not enclosed_line:
                line = "".join(collected)
                if line.strip():
                    # Not empty
                    yield line.rstrip()

    rx_soa = re.compile(
        r"^(?P<zone>\S+)\s+(?:IN\s+)?SOA\s+(\S+)\s+(\S+)\s+"
        r"(\d+)\s+(\d+[smhdw]?)+\s+(\d+[smhdw]?)+\s+(\d+[smhdw]?)+\s+(\d+[smhdw]?)+",
        re.IGNORECASE,
    )

    def iter_bind_zone_rr(self, data):
        """
        Parse bind-style zone and yields RRs
        :param data: Zone text
        """
        # ttl = None
        zone = None
        ttl = None
        seen_soa = False
        for line in self.iter_zone_lines(data):
            if line.startswith("$TTL "):
                ttl = self.parse_ttl(line[5:])
                continue
            if line.startswith("$ORIGIN "):
                zone = line[8:].strip()
                continue
            if not seen_soa:
                # Wait for SOA
                match = self.rx_soa.match(line)
                if match:
                    z = match.group("zone")
                    if z and z != "@":
                        if z.endswith("."):
                            zone = z
                        else:
                            zone = "%s.%s" % (z, zone)
                    yield RR(
                        zone=zone.strip("."),
                        name="",
                        type="SOA",
                        rdata=" ".join(match.groups()[-7:]),
                        ttl=ttl,
                    )
                    seen_soa = True
            else:
                parts = line.split()
                if parts[0] == "IN" or parts[0] in self.RR_TYPES:
                    # missed name
                    parts = [""] + parts
                # Record ttl
                if is_int(parts[1]):
                    rttl = int(parts.pop(1))
                else:
                    rttl = None
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
                if len(v) > 1 and is_int(v[0]):
                    rprio = int(v[0])
                    v = v[1:]
                else:
                    rprio = None
                value = " ".join(v)
                if t in ("CNAME", "PTR"):
                    value = self.from_idna(value)
                elif t == "TXT":
                    # Merge multiple values
                    value = self.merge_mq(value)
                yield RR(
                    zone=zone,
                    name=self.from_idna(name),
                    type=t,
                    rdata=value,
                    ttl=rttl,
                    priority=rprio,
                )

    @staticmethod
    def from_idna(s):
        """
        Convert IDNA domain name to unicode
        """
        if not s:
            return
        return ".".join(smart_text(x, encoding="idna") for x in s.split("."))

    @classmethod
    def parse_ttl(cls, line):
        """
        Parse RFC2308 TTL
        :param line:
        :return:
        """
        parts = split_alnum(line.strip())
        v = 0
        for t, mult in zip_longest(parts[::2], parts[1::2]):
            if mult is None:
                v += t
                break
            m = cls.TIMES.get(mult.lower())
            if not m:
                raise ValueError("Invalid TTL")
            v += t * m
        return v


if __name__ == "__main__":
    Command().run()
