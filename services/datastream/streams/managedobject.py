# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobject datastream
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
# NOC modules
from noc.core.datastream.base import DataStream
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface
from noc.inv.models.link import Link
from noc.inv.models.discoveryid import DiscoveryID
from noc.lib.text import split_alnum


def qs(s):
    if not s:
        return ""
    return s.encode("utf-8")


class ManagedObjectDataStream(DataStream):
    name = "managedobject"

    clean_id = DataStream.clean_id_int

    @classmethod
    def get_object(cls, id):
        mo = ManagedObject.objects.filter(id=id)[:1]
        if not mo:
            raise KeyError()
        mo = mo[0]
        r = {
            "id": str(id),
            "$version": 1,
            "bi_id": mo.bi_id,
            "name": qs(mo.name),
            "profile": qs(mo.profile.name),
            "is_managed": mo.is_managed
        }
        if mo.address:
            r["address"] = mo.address
        if mo.description:
            r["description"] = mo.description
        cls._apply_remote_system(mo, r)
        cls._apply_pool(mo, r)
        cls._apply_version(mo, r)
        cls._apply_segment(mo, r)
        cls._apply_administrative_domain(mo, r)
        cls._apply_object_profile(mo, r)
        cls._apply_chassis_id(mo, r)
        cls._apply_interfaces(mo, r)
        return r

    @staticmethod
    def _apply_pool(mo, r):
        if mo.pool:
            r["pool"] = mo.pool.name

    @staticmethod
    def _apply_remote_system(mo, r):
        if mo.remote_system:
            r["remote_system"] = {
                "id": str(mo.remote_system.id),
                "name": qs(mo.remote_system.name)
            }
            r["remote_id"] = mo.remote_id

    @staticmethod
    def _apply_version(mo, r):
        if mo.vendor:
            r["vendor"] = qs(mo.vendor.name)
            if mo.platform:
                r["platform"] = qs(mo.platform.name)
        if mo.version:
            r["version"] = qs(mo.version.name)

    @staticmethod
    def _apply_segment(mo, r):
        if not mo.segment:
            return
        r["segment"] = {
            "id": str(mo.segment.id),
            "name": qs(mo.segment.name)
        }
        if mo.segment.remote_system and mo.segment.remote_id:
            r["segment"]["remote_system"] = {
                "id": str(mo.segment.remote_system.id),
                "name": qs(mo.segment.remote_system.name)
            }
            r["segment"]["remote_id"] = mo.segment.remote_id

    @staticmethod
    def _apply_administrative_domain(mo, r):
        if not mo.administrative_domain:
            return
        r["administrative_domain"] = {
            "id": str(mo.administrative_domain.id),
            "name": qs(mo.administrative_domain.name)
        }
        if mo.administrative_domain.remote_system and mo.administrative_domain.remote_id:
            r["administrative_domain"]["remote_system"] = {
                "id": str(mo.administrative_domain.remote_system.id),
                "name": qs(mo.administrative_domain.remote_system.name)
            }
            r["administrative_domain"]["remote_id"] = mo.administrative_domain.remote_id

    @staticmethod
    def _apply_object_profile(mo, r):
        # Object profile
        r["object_profile"] = {
            "id": str(mo.object_profile.id),
            "name": qs(mo.object_profile.name)
        }
        if mo.object_profile.remote_system and mo.object_profile.remote_id:
            r["object_profile"]["remote_system"] = {
                "id": str(mo.object_profile.remote_system.id),
                "name": qs(mo.object_profile.remote_system.name)
            }
            r["object_profile"]["remote_id"] = mo.object_profile.remote_id

    @staticmethod
    def _apply_interfaces(mo, r):
        # Get interfaces
        interfaces = sorted(
            Interface.objects.filter(managed_object=mo.id),
            key=lambda x: split_alnum(x.name)
        )
        # Get subs
        subs = defaultdict(list)
        for s in SubInterface.objects.filter(managed_object=mo.id):
            subs[s.interface.id] += [s]
        # Get links
        links = defaultdict(list)
        for l in Link.objects.filter(linked_objects=mo.id):
            for li in l.interfaces:
                links[li.id] += [l]
        # Populate
        r["interfaces"] = [
            ManagedObjectDataStream._get_interface(i, subs[i.id], links[i.id])
            for i in interfaces
        ]

    @staticmethod
    def _get_interface(iface, subs, links):
        r = {
            "name": qs(iface.name),
            "type": iface.type,
            "description": qs(iface.description),
            "enabled_protocols": iface.enabled_protocols
        }
        if iface.ifindex:
            r["snmp_ifindex"] = iface.ifindex
        if iface.mac:
            r["mac"] = iface.mac
        if iface.aggregated_interface:
            r["aggregated_interface"] = iface.aggregated_interface
        # Apply profile
        if iface.profile:
            r["profile"] = ManagedObjectDataStream._get_interface_profile(iface.profile)
        # Apply subinterfaces
        subs = sorted(subs, key=lambda x: split_alnum(x.name))
        r["subinterfaces"] = [
            ManagedObjectDataStream._get_subinterface(s)
            for s in subs
        ]
        # Apply links
        if links:
            r["link"] = ManagedObjectDataStream._get_link(iface, links)
        return r

    @staticmethod
    def _get_subinterface(sub):
        r = {
            "name": qs(sub.name),
            "description": qs(sub.description),
            "enabled_afi": sub.enabled_afi,
            "enabled_protocols": sub.enabled_protocols
        }
        if sub.ifindex:
            r["snmp_ifindex"] = sub.ifindex
        if sub.mac:
            r["mac"] = sub.mac
        if sub.ipv4_addresses:
            r["ipv4_addresses"] = sub.ipv4_addresses
        if sub.ipv6_addresses:
            r["ipv6_addresses"] = sub.ipv6_addresses
        if sub.iso_addresses:
            r["iso_addresses"] = sub.iso_addresses
        if sub.vlan_ids:
            r["vlan_ids"] = sub.vlan_ids
        if sub.vpi is not None:
            r["vpi"] = sub.vpi
        if sub.vci is not None:
            r["vci"] = sub.vci
        if sub.untagged_vlan:
            r["untagged_vlan"] = sub.untagged_vlan
        if sub.tagged_vlans:
            r["tagged_vlans"] = sub.tagged_vlans
        return r

    @staticmethod
    def _get_link(iface, links):
        r = []
        for link in links:
            rr = []
            for i in link.interfaces:
                if i.managed_object.id == iface.managed_object.id:
                    continue
                rr += [{
                    "object": str(i.managed_object.id),
                    "interface": qs(i.name),
                    "method": link.discovery_method
                }]
            r += [rr]
        return r

    @staticmethod
    def _get_interface_profile(profile):
        return {
            "id": str(profile.id),
            "name": qs(profile.name)
        }

    @staticmethod
    def _apply_chassis_id(mo, r):
        di = DiscoveryID.objects.filter(object=mo.id).first()
        if not di:
            return
        rr = {}
        if di.hostname:
            rr["hostname"] = str(di.hostname)
        if di.chassis_mac:
            rr["macs"] = [{"first": m.first_mac, "last": m.last_mac} for m in di.chassis_mac]
        if di.router_id:
            rr["router_id"] = di.router_id
        if di.udld_id:
            rr["udld_id"] = di.router_id
        if rr:
            r["chassis_id"] = rr
