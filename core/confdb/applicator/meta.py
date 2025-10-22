# ----------------------------------------------------------------------
# MetaApplicator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from noc.inv.models.discoveryid import DiscoveryID
from noc.inv.models.resourcegroup import ResourceGroup
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.core.script.scheme import PROTOCOLS
from noc.core.matcher import match
from .base import BaseApplicator


class MetaApplicator(BaseApplicator):
    def apply(self):
        self.confdb.insert_bulk(self.iter_object_meta())
        self.confdb.insert_bulk(self.iter_interfaces_meta())
        self.confdb.insert_bulk(self.chassis_mac_meta())

    def iter_object_meta(self):
        """
        Yields `meta` node
        :return:
        """
        # meta id
        yield "meta", "id", str(self.object.id)
        # meta name
        yield "meta", "name", str(self.object.name)
        # meta description
        yield "meta", "description", str(self.object.description or "")
        # meta profile
        yield "meta", "profile", self.object.profile.name
        # meta vendor
        if self.object.vendor:
            yield "meta", "vendor", self.object.vendor.code[0]
        # meta platform
        if self.object.platform:
            yield "meta", "platform", self.object.platform.name
        # meta version
        if self.object.version:
            yield "meta", "version", self.object.version.version
        # meta object-profile
        yield "meta", "object-profile", "id", str(self.object.object_profile.id)
        yield "meta", "object-profile", "name", self.object.object_profile.name
        yield "meta", "object-profile", "level", str(self.object.object_profile.level)
        # meta segment
        yield "meta", "segment", "id", str(self.object.segment.id)
        yield "meta", "segment", "name", self.object.segment.name
        # meta administrative domain
        for ad in AdministrativeDomain.objects.filter(
            id__in=self.object.administrative_domain.get_path()
        ):
            yield "meta", "administrative-domains", ad.name, "id", str(ad.id)
        # meta management
        yield "meta", "management", "address", self.object.address
        yield "meta", "management", "protocol", PROTOCOLS[self.object.scheme]
        yield "meta", "management", "pool", str(self.object.pool.name)
        if self.object.vrf:
            yield "meta", "management", "vrf", "id", str(self.object.vrf.id)
            yield "meta", "management", "vrf", "name", str(self.object.vrf.name)
        # Client groups
        if self.object.static_client_groups or self.object.static_service_groups:
            for group in ResourceGroup.objects.filter(
                id__in=self.object.static_client_groups + self.object.static_service_groups
            ):
                if str(group.id) in self.object.static_client_groups:
                    yield "meta", "client-groups", group.name, "id", str(group.id)
                    yield "meta", "client-groups", group.name, "technology", group.technology.name
                else:
                    yield "meta", "service-groups", group.name, "id", str(group.id)
                    yield "meta", "service-groups", group.name, "technology", group.technology.name
        # meta labels
        if self.object.labels:
            for label in self.object.labels:
                yield "meta", "labels", label
        # meta matchers
        if self.object.version:
            yield from self.iter_object_meta_matchers()

    def iter_object_meta_matchers(self):
        ctx = {
            "vendor": self.object.vendor.name,
            "platform": self.object.platform.name,
            "version": self.object.version.version,
        }
        for matcher in self.object.get_profile().matchers:
            if match(ctx, self.object.get_profile().matchers[matcher]):
                yield "meta", "matchers", matcher

    def chassis_mac_meta(self):
        ch_id = DiscoveryID.objects.filter(object=self.object.id).first()
        ch_macs = ch_id.chassis_mac if ch_id else []
        for n, mac in enumerate(ch_macs):
            mac1 = mac.first_mac
            mac2 = mac.last_mac
            yield "meta", "chassis_id", n, "range", mac1, mac2

    def iter_interfaces_meta(self):
        # Get all interfaces
        ifaces = {
            iface.name: iface for iface in Interface.objects.filter(managed_object=self.object.id)
        }
        own_ifaces = {ifaces[iface].id for iface in ifaces}
        # Get all links
        links = {}  # interface -> object -> [remote_interface, ...]
        for link in Link.object_links(self.object):
            local_interfaces = set()
            remote_interfaces = {}  # object -> [interfaces]
            for i in link.interfaces:
                if i.id in own_ifaces:
                    local_interfaces.add(i.name)
                else:
                    if i.managed_object not in remote_interfaces:
                        remote_interfaces[i.managed_object] = []
                    remote_interfaces[i.managed_object] += [i.name]
            for li in local_interfaces:
                links[li] = remote_interfaces
        # Yield meta for all interfaces
        for ctx in self.confdb.query("Match('interfaces', ifname)"):
            iface = ifaces.get(ctx["ifname"])
            if not iface:
                continue
            # interfaces X meta profile
            if iface.profile:
                yield "interfaces", iface.name, "meta", "profile", "id", str(iface.profile.id)
                yield "interfaces", iface.name, "meta", "profile", "name", iface.profile.name
            if iface.ifindex is not None:
                yield "interfaces", iface.name, "meta", "ifindex", int(iface.ifindex)
            if iface.mac:
                yield "interfaces", iface.name, "meta", "mac", str(iface.mac)
            # interfaces X meta hints
            if iface.hints:
                for hint in iface.hints:
                    yield "interfaces", iface.name, "meta", "hints", hint
            # interfaces X meta link
            if iface.name in links:
                for n, ro in enumerate(sorted(links[iface.name], key=str)):
                    n = str(n)
                    yield "interfaces", iface.name, "meta", "link", n, "object", "id", str(ro.id)
                    yield "interfaces", iface.name, "meta", "link", n, "object", "name", ro.name
                    yield (
                        "interfaces",
                        iface.name,
                        "meta",
                        "link",
                        n,
                        "object",
                        "profile",
                        "id",
                        str(ro.object_profile.id),
                    )
                    yield (
                        "interfaces",
                        iface.name,
                        "meta",
                        "link",
                        n,
                        "object",
                        "profile",
                        "name",
                        ro.object_profile.name,
                    )
                    yield (
                        "interfaces",
                        iface.name,
                        "meta",
                        "link",
                        n,
                        "object",
                        "profile",
                        "level",
                        ro.object_profile.level,
                    )
                    for ri in sorted(links[iface.name][ro]):
                        yield "interfaces", iface.name, "meta", "link", n, "interface", ri
