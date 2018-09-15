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
from noc.inv.models.resourcegroup import ResourceGroup
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.objectcapabilities import ObjectCapabilities
from noc.inv.models.interfaceprofile import InterfaceProfile
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
        cls._apply_caps(mo, r)
        cls._apply_segment(mo, r)
        cls._apply_administrative_domain(mo, r)
        cls._apply_object_profile(mo, r)
        cls._apply_chassis_id(mo, r)
        cls._apply_interfaces(mo, r)
        cls._apply_resource_groups(mo, r)
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
            r["version"] = qs(mo.version.version)

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
    def _apply_caps(mo, r):
        # Get caps
        cdata = ObjectCapabilities.get_capabilities(mo)
        if not cdata:
            return
        caps = []
        for cname in sorted(cdata):
            caps += [{
                "name": cname,
                "value": str(cdata[cname])
            }]
        r["capabilities"] = caps

    @staticmethod
    def _apply_interfaces(mo, r):
        # id -> (object id, name)
        ifcache = {}
        # Get interfaces
        interfaces = sorted(
            Interface._get_collection().find({"managed_object": mo.id}),
            key=lambda x: split_alnum(x["name"])
        )
        # Populate cache
        for i in interfaces:
            ifcache[i["_id"]] = (i["managed_object"], i["name"])
        # Get subs
        subs = defaultdict(list)
        for s in SubInterface._get_collection().find({"managed_object": mo.id}):
            subs[s["interface"]] += [s]
        # Get links
        links = defaultdict(list)
        for l in Link._get_collection().find({"linked_objects": mo.id}):
            for li in l.get("interfaces", []):
                links[li] += [l]
        # Populate cache with linked interfaces
        if links:
            for i in Interface._get_collection().find({
                "_id": {"$in": list(links)}
            }, {
                "_id": 1,
                "managed_object": 1,
                "name": 1
            }):
                ifcache[i["_id"]] = (i["managed_object"], i["name"])
        # Populate
        r["interfaces"] = [
            ManagedObjectDataStream._get_interface(i, subs[i["_id"]], links[i["_id"]], ifcache)
            for i in interfaces
        ]

    @staticmethod
    def _get_interface(iface, subs, links, ifcache):
        r = {
            "name": qs(iface["name"]),
            "type": iface["type"],
            "description": qs(iface.get("description")),
            "enabled_protocols": iface.get("enabled_protocols") or []
        }
        if iface.get("ifindex"):
            r["snmp_ifindex"] = iface["ifindex"]
        if iface.get("mac"):
            r["mac"] = iface["mac"]
        if iface.get("aggregated_interface"):
            r["aggregated_interface"] = ifcache[iface["aggregated_interface"]][-1]
        # Apply profile
        if iface.get("profile"):
            profile = InterfaceProfile.get_by_id(iface["profile"])
            r["profile"] = ManagedObjectDataStream._get_interface_profile(profile)
        # Apply subinterfaces
        r["subinterfaces"] = [
            ManagedObjectDataStream._get_subinterface(s)
            for s in sorted(subs, key=lambda x: split_alnum(x["name"]))
        ]
        # Apply links
        if links:
            r["link"] = ManagedObjectDataStream._get_link(iface, links, ifcache)
        return r

    @staticmethod
    def _get_subinterface(sub):
        r = {
            "name": qs(sub["name"]),
            "description": qs(sub.get("description")),
            "enabled_afi": sub.get("enabled_afi") or [],
            "enabled_protocols": sub.get("enabled_protocols") or []
        }
        if sub.get("ifindex"):
            r["snmp_ifindex"] = sub["ifindex"]
        if sub.get("mac"):
            r["mac"] = sub["mac"]
        if sub.get("ipv4_addresses"):
            r["ipv4_addresses"] = sub["ipv4_addresses"]
        if sub.get("ipv6_addresses"):
            r["ipv6_addresses"] = sub["ipv6_addresses"]
        if sub.get("iso_addresses"):
            r["iso_addresses"] = sub["iso_addresses"]
        if sub.get("vlan_ids"):
            r["vlan_ids"] = sub["vlan_ids"]
        if sub.get("vpi") is not None:
            r["vpi"] = sub["vpi"]
        if sub.get("vci") is not None:
            r["vci"] = sub["vci"]
        if sub.get("untagged_vlan"):
            r["untagged_vlan"] = sub["untagged_vlan"]
        if sub.get("tagged_vlans"):
            r["tagged_vlans"] = sub["tagged_vlans"]
        return r

    @staticmethod
    def _get_link(iface, links, ifcache):
        r = []
        for link in links:
            for i in link["interfaces"]:
                ro, rname = ifcache[i]
                if ro == iface["managed_object"]:
                    continue
                r += [{
                    "object": str(ro),
                    "interface": qs(rname),
                    "method": link.get("discovery_method") or ""
                }]
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

    @staticmethod
    def _apply_resource_groups(mo, r):
        if mo.effective_service_groups:
            r["service_groups"] = ManagedObjectDataStream._get_resource_groups(
                mo.effective_service_groups,
                mo.static_service_groups
            )
        if mo.effective_client_groups:
            r["client_groups"] = ManagedObjectDataStream._get_resource_groups(
                mo.effective_client_groups,
                mo.static_client_groups
            )

    @staticmethod
    def _get_resource_groups(groups, static_groups):
        r = []
        for g in groups:
            rg = ResourceGroup.get_by_id(g)
            if not rg:
                continue
            r += [{
                "id": str(g),
                "name": qs(rg.name),
                "technology": qs(rg.technology.name),
                "static": g in static_groups
            }]
        return r

    @classmethod
    def get_meta(cls, data):
        return {
            "pool": data.get("pool"),
            "service_groups": [g["id"] for g in data.get("service_groups", [])],
            "client_groups": [g["id"] for g in data.get("client_groups", [])]
        }

    @classmethod
    def filter_pool(cls, name):
        return {
            "%s.pool" % cls.F_META: name
        }

    @classmethod
    def filter_service_group(cls, name):
        return {
            "%s.service_groups" % cls.F_META: name
        }

    @classmethod
    def filter_client_group(cls, name):
        return {
            "%s.client_groups" % cls.F_META: name
        }
