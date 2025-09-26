# ----------------------------------------------------------------------
# dnszone DataStream
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from collections import defaultdict
from itertools import chain
from typing import Iterable

# Third-party modules
from django.db.models import Q

# NOC modules
from noc.core.ip import IPv6
from noc.core.datastream.base import DataStream
from noc.main.models.systemtemplate import SystemTemplate
from noc.dns.models.dnszone import DNSZone, ZONE_FORWARD, ZONE_REVERSE_IPV4, ZONE_REVERSE_IPV6
from noc.dns.models.dnszonerecord import DNSZoneRecord
from ..models.dnszone import DNSZoneDataStreamItem
from noc.ip.models.address import Address
from noc.ip.models.addressrange import AddressRange
from noc.core.dns.rr import RR
from noc.core.dns.zonefile import ZoneFile
from noc.core.dns.encoding import to_idna


class DNSZoneDataStream(DataStream):
    name = "dnszone"
    model = DNSZoneDataStreamItem
    clean_id = DataStream.clean_id_int

    @staticmethod
    def non_dotted(s: str) -> str:
        if s.endswith("."):
            return str(s[:-1])
        return str(s)

    @classmethod
    def get_object(cls, id):
        zone = DNSZone.objects.filter(id=id)[:1]
        if not zone:
            raise KeyError()
        zone = zone[0]
        return {
            "id": str(zone.id),
            "name": str(zone.name),
            "serial": str(zone.serial),
            "masters": [cls.non_dotted(x) for x in zone.masters],
            "slaves": [cls.non_dotted(x) for x in zone.slaves],
            "records": cls.get_records(zone),
        }

    @classmethod
    def get_records(cls, zone: DNSZone):
        """
        Get zone records
        :param zone:
        :return:
        """
        zone_iters = [cls.iter_soa(zone)]
        if zone.type == ZONE_FORWARD:
            zone_iters += [sorted(cls.iter_forward(zone))]
        elif zone.type == ZONE_REVERSE_IPV4:
            zone_iters += [sorted(cls.iter_reverse_ipv4(zone))]
        elif zone.type == ZONE_REVERSE_IPV6:
            zone_iters += [sorted(cls.iter_reverse_ipv6(zone))]
        return [x.to_json() for x in chain(*tuple(zone_iters))]

    @classmethod
    def iter_soa(cls, zone: DNSZone) -> Iterable[RR]:
        """
        Yield SOA record
        :return:
        """

        def dotted(s):
            if not s.endswith("."):
                return s + "."
            return s

        yield RR(
            zone=zone.name,
            name=dotted(to_idna(zone.name)),
            ttl=zone.profile.zone_ttl,
            type="SOA",
            rdata="%s %s %d %d %d %d %d"
            % (
                dotted(zone.profile.zone_soa),
                dotted(zone.profile.zone_contact),
                zone.serial,
                zone.profile.zone_refresh,
                zone.profile.zone_retry,
                zone.profile.zone_expire,
                zone.profile.zone_ttl,
            ),
        )

    @classmethod
    def iter_ns(cls, zone: DNSZone) -> Iterable[RR]:
        """
        Yield NS records
        :param zone:
        :return:
        """
        for ns in zone.ns_list:
            yield RR(zone=zone.name, name="", ttl=zone.profile.zone_ttl, type="NS", rdata=ns)

    @classmethod
    def iter_forward(cls, zone: DNSZone) -> Iterable[RR]:
        """
        Yield forward zone records
        :param zone:
        :return:
        """
        return chain(
            cls.iter_ns(zone),
            cls.iter_rr(zone),
            cls.iter_ipam_a(zone),
            cls.iter_missed_ns_a(zone),
            cls.iter_nested_ns(zone),
        )

    @classmethod
    def iter_reverse_ipv4(cls, zone):
        """
        Yield IPv4 reverse zone
        :param zone:
        :return:
        """
        return chain(
            cls.iter_ns(zone),
            cls.iter_rr(zone),
            cls.iter_ipam_ptr4(zone),
            cls.iter_classless_delegation(zone),
        )

    @classmethod
    def iter_reverse_ipv6(cls, zone):
        """
        Yield IPv6 reverse zone
        :param zone:
        :return:
        """
        return chain(cls.iter_ns(zone), cls.iter_rr(zone), cls.iter_ipam_ptr6(zone))

    @classmethod
    def iter_nested_ns(cls, zone: DNSZone) -> Iterable[RR]:
        """
        Yield NS/A records for nested zones
        :param zone:
        :return:
        """
        suffix = ".%s." % zone.name
        length = len(zone.name)
        for z in zone.children:
            nested_nses = set()
            for ns in z.profile.authoritative_servers:
                # NS record
                ns_name = zone.get_ns_name(ns)
                yield RR(
                    zone=zone.name,
                    name=z.name[: -length - 1],
                    ttl=zone.profile.zone_ttl,
                    type="NS",
                    rdata=ns_name,
                )
                # Zone delegated to NS from the child zone
                if ns_name.endswith(suffix) and "." in ns_name[: -len(suffix)]:
                    nested_nses.add((ns_name[: -len(suffix)], ns.ip))
            # Yield glue A records for nested NSs
            for name, ip in nested_nses:
                yield RR(zone=zone.name, name=name, ttl=z.profile.zone_ttl, type="A", rdata=ip)

    @classmethod
    def iter_rr(cls, zone: DNSZone) -> Iterable[RR]:
        """
        Yield directly set RRs from database
        :return:
        """
        for zr in DNSZoneRecord.objects.filter(zone=zone):
            if "/" in zr.name:
                continue
            if not zr.type or not zr.content:
                continue
            yield RR(
                zone=zone.name,
                name=zr.name,
                type=zr.type,
                ttl=zr.ttl if zr.ttl else zone.profile.zone_ttl,
                priority=zr.priority,
                rdata=zr.content,
            )

    @classmethod
    def iter_ipam_a(cls, zone: DNSZone) -> Iterable[RR]:
        """
        Yield A/AAAA records from IPAM
        :return: (name, type, content, ttl, prio)
        """
        # @todo: Filter by VRF
        # @todo: Filter by profile
        # @todo: Get ttl from profile
        # Build query
        length = len(zone.name) + 1
        q = Q(fqdn__iexact=zone.name) | Q(fqdn__iendswith=".%s" % zone.name)
        for z in DNSZone.objects.filter(name__iendswith=".%s" % zone.name).values_list(
            "name", flat=True
        ):
            q &= ~(Q(fqdn__iexact=z) | Q(fqdn__iendswith=".%s" % z))
        for afi, fqdn, address in Address.objects.filter(q).values_list("afi", "fqdn", "address"):
            yield RR(
                zone=zone.name,
                name=fqdn[:-length],
                type="A" if afi == "4" else "AAAA",
                ttl=zone.profile.zone_ttl,
                rdata=address,
            )

    @classmethod
    def iter_ipam_ptr4(cls, zone: DNSZone) -> Iterable[RR]:
        """
        Yield IPv4 PTR records from IPAM
        :param zone:
        :return:
        """

        def ptr(a):
            """
            Convert address to full PTR record
            """
            x = a.split(".")
            x.reverse()
            return "%s.in-addr.arpa" % (".".join(x))

        length = len(zone.name) + 1
        for a in Address.objects.filter(afi="4").extra(
            where=["address << %s"], params=[zone.reverse_prefix]
        ):
            if not a.fqdn:
                continue
            yield RR(
                zone=zone.name,
                name=ptr(a.address)[:-length],
                ttl=zone.profile.zone_ttl,
                type="PTR",
                rdata=a.fqdn + ".",
            )

    @classmethod
    def iter_ipam_ptr6(cls, zone: DNSZone) -> Iterable[RR]:
        """
        Yield IPv6 PTR records from IPAM
        :return: (name, type, content, ttl, prio)
        :return:
        """
        origin_length = (len(zone.name) - 8 + 1) // 2
        for a in Address.objects.filter(afi="6").extra(
            where=["address << %s"], params=[zone.reverse_prefix]
        ):
            yield RR(
                zone=zone.name,
                name=IPv6(a.address).ptr(origin_length),
                ttl=zone.profile.zone_ttl,
                type="PTR",
                rdata=a.fqdn + ".",
            )

    @classmethod
    def iter_missed_ns_a(cls, zone: DNSZone) -> Iterable[RR]:
        """
        Yield missed A record for NS'es
        :param zone:
        :return:
        """
        suffix = ".%s." % zone.name
        # Create missed A records for NSses from zone
        # Find in-zone NSes
        in_zone_nses = {}
        for ns in zone.profile.authoritative_servers:
            if not ns.ip:
                continue
            ns_name = zone.get_ns_name(ns)
            # NS server from zone
            if ns_name.endswith(suffix) and "." not in ns_name[: -len(suffix)]:
                in_zone_nses[ns_name[: -len(suffix)]] = ns.ip
        # Find missed in-zone NSes
        for name in in_zone_nses:
            yield RR(
                zone=zone.name,
                name=name,
                type="A",
                ttl=zone.profile.zone_ttl,
                rdata=in_zone_nses[name],
            )

    @classmethod
    def iter_classless_delegation(cls, zone: DNSZone) -> RR:
        """
        Yield classless zone delegations
        :return:
        """
        # Range delegations
        for r in AddressRange.objects.filter(action="D").extra(
            where=["from_address << %s", "to_address << %s"],
            params=[zone.reverse_prefix, zone.reverse_prefix],
        ):
            nses = [ns.strip() for ns in r.reverse_nses.split(",")]
            for a in r.addresses:
                n = a.address.split(".")[-1]
                yield RR(
                    zone=zone.name,
                    name=n,
                    ttl=zone.profile.zone_ttl,
                    type="CNAME",
                    rdata="%s.%s/32" % (n, n),
                )
                for ns in nses:
                    if not ns.endswith("."):
                        ns += "."
                    yield RR(
                        zone=zone.name,
                        name="%s/32" % n,
                        ttl=zone.profile.zone_ttl,
                        type="NS",
                        rdata=ns,
                    )
        # Subnet delegation macro
        delegations = defaultdict(list)
        for zr in DNSZoneRecord.objects.filter(zone=zone, type="NS", name__contains="/"):
            delegations[zr.name] += [zr.content]
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
                yield RR(zone=zone.name, name=d, ttl=zone.profile.zone_ttl, type="NS", rdata=ns)
            m = mask - 24
            bitmask = ((1 << m) - 1) << (8 - m)
            if net & bitmask != net:
                continue  # Invalid network
            for i in range(net, net + (1 << (8 - m))):
                yield RR(
                    zone=zone.name,
                    name=str(i),
                    ttl=zone.profile.zone_ttl,
                    type="CNAME",
                    rdata="%d.%s" % (i, d),
                )

    @classmethod
    def on_change(cls, data):
        """
        DNS Zone changed, increase serial

        :param data:
        :return:
        """
        zone = DNSZone.objects.filter(id=data["id"])[:1]
        if not zone:
            return None
        zone = zone[0]
        zone.set_next_serial()
        # Update data
        data["serial"] = str(zone.serial)
        # Update SOA record
        soa = list(data["records"][0]["rdata"].split())
        soa[2] = str(zone.serial)
        data["records"][0]["rdata"] = " ".join(soa)
        # Prepare notification groups
        ngroups = zone.get_notification_groups()
        # Render and write zone text
        if ngroups:
            cz = zone.zone.read()
        zt = ZoneFile(data).get_text()
        zone.zone.write(zt)
        # Notify changes
        if ngroups:
            ctx = {"name": zone.name}
            if cz:
                revs = zone.zone.get_revisions()[-2:]
                stpl = "dns.zone.change"
                ctx["diff"] = zone.zone.diff(revs[0], revs[1])
            else:
                stpl = "dns.zone.new"
                ctx["data"] = zt
            try:
                t = SystemTemplate.objects.get(name=stpl)
            except SystemTemplate.DoesNotExist:
                return True
            subject = t.render_subject(**ctx)
            body = t.render_body(**ctx)
            for g in ngroups:
                g.notify(subject, body)
        return True

    @classmethod
    def get_meta(cls, data):
        return {"servers": data.get("masters", []) + data.get("slaves", [])}

    @classmethod
    def filter_server(cls, name):
        return {f"{cls.F_META}.servers": {"$elemMatch": {"$elemMatch": {"$in": [name]}}}}
