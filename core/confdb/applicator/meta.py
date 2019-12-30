# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# MetaApplicator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# NOC modules
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from noc.core.script.scheme import PROTOCOLS
from .base import BaseApplicator


class MetaApplicator(BaseApplicator):
    def apply(self):
        self.confdb.insert_bulk(self.iter_object_meta())
        self.confdb.insert_bulk(self.iter_interfaces_meta())

    def iter_object_meta(self):
        """
        Yields `meta` node
        :return:
        """
        # meta id
        yield "meta", "id", str(self.object.id)
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
        # meta management
        yield "meta", "management", "address", self.object.address
        yield "meta", "management", "protocol", PROTOCOLS[self.object.scheme]
        # meta tags
        if self.object.tags:
            for tag in self.object.tags:
                yield "meta", "tags", tag

    def iter_interfaces_meta(self):
        # Get all interfaces
        ifaces = dict(
            (iface.name, iface) for iface in Interface.objects.filter(managed_object=self.object.id)
        )
        own_ifaces = set(ifaces[iface].id for iface in ifaces)
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
                for n, ro in enumerate(sorted(links[iface.name])):
                    n = str(n)
                    yield "interfaces", iface.name, "meta", "link", n, "object", "id", str(ro.id)
                    yield "interfaces", iface.name, "meta", "link", n, "object", "name", ro.name
                    yield "interfaces", iface.name, "meta", "link", n, "object", "profile", "id", str(
                        ro.object_profile.id
                    )
                    yield "interfaces", iface.name, "meta", "link", n, "object", "profile", "name", ro.object_profile.name
                    yield "interfaces", iface.name, "meta", "link", n, "object", "profile", "level", ro.object_profile.level
                    for ri in sorted(links[iface.name][ro]):
                        yield "interfaces", iface.name, "meta", "link", n, "interface", ri
