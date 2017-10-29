# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ManagedObject card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import operator
# Third-party modules
from django.db.models import Q
# NOC modules
from base import BaseCard
from noc.sa.models.managedobject import ManagedObject
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.uptime import Uptime
from noc.fm.models.outage import Outage
from noc.inv.models.object import Object
from noc.inv.models.discoveryid import DiscoveryID
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from noc.sa.models.service import Service
from noc.inv.models.firmwarepolicy import FirmwarePolicy
from noc.sa.models.servicesummary import ServiceSummary
from noc.lib.text import split_alnum, list_to_ranges
from noc.maintenance.models.maintenance import Maintenance
from noc.sa.models.useraccess import UserAccess


class ManagedObjectCard(BaseCard):
    name = "managedobject"
    default_template_name = "managedobject"
    model = ManagedObject

    def get_object(self, id):
        if self.current_user.is_superuser:
            return ManagedObject.objects.get(id=id)
        else:
            return ManagedObject.objects.get(
                id=id,
                administrative_domain__in=self.get_user_domains()
            )

    def get_template_name(self):
        return self.object.object_profile.card or "managedobject"

    def get_data(self):
        if not self.object:
            return None
        # @todo: Stage
        # @todo: Service range
        # @todo: Open TT
        now = datetime.datetime.now()
        # Get object status and uptime
        alarms = list(ActiveAlarm.objects.filter(managed_object=self.object.id))
        current_start = None
        duration = None
        if self.object.get_status():
            if alarms:
                current_state = "alarm"
            else:
                current_state = "up"
            uptime = Uptime.objects.filter(
                object=self.object.id,
                stop=None
            ).first()
            if uptime:
                current_start = uptime.start
        else:
            current_state = "down"
            outage = Outage.objects.filter(
                object=self.object.id,
                stop=None
            ).first()
            if outage:
                current_start = outage.start
        if current_start:
            duration = now - current_start
        # Get container path
        cp = []
        if self.object.container:
            c = self.object.container.id
            while c:
                try:
                    o = Object.objects.get(id=c)
                    # @todo: Address data
                    if o.container:
                        cp.insert(0, {
                            "id": o.id,
                            "name": o.name
                        })
                    c = o.container
                except Object.DoesNotExist:
                    break
        # MAC addresses
        macs = []
        o_macs = DiscoveryID.macs_for_object(self.object)
        if o_macs:
            for f, l in o_macs:
                if f == l:
                    macs += [f]
                else:
                    macs += ["%s - %s" % (f, l)]
        # Links
        uplinks = set(self.object.data.uplinks)
        if len(uplinks) > 1:
            if self.object.segment.lost_redundancy:
                redundancy = "L"
            else:
                redundancy = "R"
        else:
            redundancy = "N"
        links = []
        for l in Link.object_links(self.object):
            local_interfaces = []
            remote_interfaces = []
            remote_objects = set()
            for i in l.interfaces:
                if i.managed_object.id == self.object.id:
                    local_interfaces += [i]
                else:
                    remote_interfaces += [i]
                    remote_objects.add(i.managed_object)
            if len(remote_objects) == 1:
                ro = remote_objects.pop()
                if ro.id in uplinks:
                    role = "uplink"
                else:
                    role = "downlink"
                links += [{
                    "id": l.id,
                    "role": role,
                    "local_interface": sorted(
                        local_interfaces,
                        key=lambda x: split_alnum(x.name)
                    ),
                    "remote_object": ro,
                    "remote_interface": sorted(
                        remote_interfaces,
                        key=lambda x: split_alnum(x.name)
                    ),
                    "remote_status": "up" if ro.get_status() else "down"
                }]
            links = sorted(links, key=lambda x: (x["role"] != "uplink", split_alnum(x["local_interface"][0])))
        # Build global services summary
        service_summary = ServiceSummary.get_object_summary(
            self.object)
        # Interfaces
        interfaces = []
        for i in Interface.objects.filter(managed_object=self.object.id,
                                          type="physical"):
            interfaces += [{
                "id": i.id,
                "name": i.name,
                "admin_status": i.admin_status,
                "oper_status": i.oper_status,
                "mac": i.mac,
                "full_duplex": i.full_duplex,
                "speed": max([i.in_speed or 0, i.out_speed or 0]) / 1000,
                "untagged_vlan": None,
                "tagged_vlan": None,
                "service": i.service,
                "service_summary": service_summary.get("interface").get(i.id, {})
            }]
            si = list(i.subinterface_set.filter(enabled_afi="BRIDGE"))
            if len(si) == 1:
                si = si[0]
                interfaces[-1]["untagged_vlan"] = si.untagged_vlan
                interfaces[-1]["tagged_vlans"] = list_to_ranges(si.tagged_vlans).replace(",", ", ")
        interfaces = sorted(interfaces, key=lambda x: split_alnum(x["name"]))
        # Termination group
        l2_terminators = []
        if self.object.termination_group:
            l2_terminators = list(
                ManagedObject.objects.filter(service_terminator=self.object.termination_group)
            )
            l2_terminators = sorted(l2_terminators, key=operator.attrgetter("name"))
        # @todo: Administrative domain path
        # Alarms
        alarm_list = []
        for a in alarms:
            alarm_list += [{
                "id": a.id,
                "timestamp": a.timestamp,
                "duration": now - a.timestamp,
                "subject": a.subject
            }]
        alarm_list = sorted(alarm_list, key=operator.itemgetter("timestamp"))
        # Maintenance
        maintenance = []
        for m in Maintenance.objects.filter(
            affected_objects__object=self.object.id,
            is_completed=False,
            start__lte=now + datetime.timedelta(hours=1)
        ):
            maintenance += [{
                "maintenance": m,
                "id": m.id,
                "subject": m.subject,
                "start": m.start,
                "stop": m.stop,
                "in_progress": m.start <= now
            }]
        # Get Inventory
        inv = []
        for p in self.object.get_inventory():
            c = self.get_nested_inventory(p)
            c["name"] = p.name or self.object.name
            inv += [c]
        # Build result
        r = {
            "id": self.object.id,
            "object": self.object,
            "name": self.object.name,
            "address": self.object.address,
            "platform": self.object.platform.name if self.object.platform else "Unknown",
            "version": self.object.version.version if self.object.version else "",
            "description": self.object.description,
            "object_profile": self.object.object_profile.id,
            "object_profile_name": self.object.object_profile.name,
            "macs": ", ".join(sorted(macs)),
            "segment": self.object.segment,
            "firmware_status": FirmwarePolicy.get_status(self.object.platform, self.object.version),
            "firmware_recommended": FirmwarePolicy.get_recommended_version(self.object.platform),
            "service_summary": service_summary,
            #
            "container_path": cp,
            #
            "current_state": current_state,
            # Start of uptime/downtime
            "current_start": current_start,
            # Current uptime/downtime
            "current_duration": duration,
            "l2_terminators": l2_terminators,
            "tt": [],
            "links": links,
            "alarms": alarm_list,
            "interfaces": interfaces,
            "maintenance": maintenance,
            "redundancy": redundancy,
            "inventory": self.flatten_inventory(inv)
        }
        return r

    def get_service_glyphs(self, service):
        """
        Returns a list of (service profile name, glyph)
        """
        r = []
        if service.logical_status in ("T", "R", "S"):
            if service.profile.glyph:
                r += [(service.profile.name, service.profile.glyph)]
            for svc in Service.objects.filter(parent=service):
                r += self.get_service_glyphs(svc)
        return r

    @classmethod
    def search(cls, handler, query):
        q = Q(name__icontains=query)
        sq = ManagedObject.get_search_Q(query)
        if sq:
            q |= sq
        if not handler.current_user.is_superuser:
            q &= UserAccess.Q(handler.current_user)
        r = []
        for mo in ManagedObject.objects.filter(q):
            r += [{
                "scope": "managedobject",
                "id": mo.id,
                "label": "%s (%s) [%s]" % (mo.name, mo.address, mo.platform)
            }]
        return r

    def get_nested_inventory(self, o):
        rev = o.get_data("asset", "revision")
        if rev == "None":
            rev = ""
        r = {
            "id": str(o.id),
            "serial": o.get_data("asset", "serial"),
            "revision": rev or "",
            "description": o.model.description,
            "model": o.model.name,
            "children": []
        }
        for n in o.model.connections:
            if n.direction == "i":
                c, r_object, _ = o.get_p2p_connection(n.name)
                if c is None:
                    r["children"] += [{
                        "id": "",
                        "name": n.name,
                        "serial": "",
                        "description": "--- EMPTY ---",
                        "model": ""
                    }]
                else:
                    cc = self.get_nested_inventory(r_object)
                    cc["name"] = n.name
                    r["children"] += [cc]
            elif n.direction == "s":
                r["children"] += [{
                    "id": "",
                    "name": n.name,
                    "serial": "",
                    "description": n.description,
                    "model": ", ".join(n.protocols)
                }]
        return r

    def flatten_inventory(self, inv, level=0):
        r = []
        if not isinstance(inv, list):
            inv = [inv]
        for o in inv:
            r += [o]
            o["level"] = level
            children = o.get("children", [])
            if children:
                for c in children:
                    r += self.flatten_inventory(c, level + 1)
                del o["children"]
        return r
