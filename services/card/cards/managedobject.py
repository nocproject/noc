# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ManagedObject card handler
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import operator
## NOC modules
from base import BaseCard
from noc.sa.models.managedobject import ManagedObject
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.uptime import Uptime
from noc.fm.models.outage import Outage
from noc.inv.models.object import Object
from noc.inv.models.discoveryid import DiscoveryID
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from noc.inv.models.objectuplink import ObjectUplink
from noc.sa.models.service import Service
from noc.lib.text import split_alnum, list_to_ranges


class ManagedObjectCard(BaseCard):
    default_template_name = "managedobject"
    model = ManagedObject

    def get_template_name(self):
        return self.object.object_profile.card or "managedobject"

    def get_data(self):
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
        uplinks = ObjectUplink.objects.filter(object=self.object.id).first()
        if uplinks:
            uplinks = set(uplinks.uplinks)
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
        # Interfaces
        interfaces = []
        for i in Interface.objects.filter(managed_object=self.object.id,
                                          type="physical"):
            interfaces += [{
                "id": i.id,
                "name": i.name,
                "admin_status": i.admin_status,
                "oper_status": i.oper_status,
                "full_duplex": i.full_duplex,
                "speed": max([i.in_speed or 0, i.out_speed or 0]) / 1000,
                "untagged_vlan": None,
                "tagged_vlan": None,
                "service": i.service,
                "service_summary": []
            }]
            si = list(i.subinterface_set.filter(enabled_afi="BRIDGE"))
            if len(si) == 1:
                si = si[0]
                interfaces[-1]["untagged_vlan"] = si.untagged_vlan
                interfaces[-1]["tagged_vlans"] = list_to_ranges(si.tagged_vlans).replace(",", ", ")
            # Build service summary
            if i.service:
                ss = []
                sr = {}
                for pname, glyph in self.get_service_glyphs(i.service):
                    if pname in sr:
                        sr[pname]["count"] += 1
                    else:
                        sr[pname] = {
                            "name": pname,
                            "glyph": glyph,
                            "count": 1
                        }
                        ss += [sr[pname]]
                interfaces[-1]["service_summary"] = ss
        interfaces = sorted(interfaces, key=lambda x: split_alnum(x["name"]))
        # Build global services summary
        service_summary = []
        sr = {}
        for i in interfaces:
            for s in i["service_summary"]:
                if s["name"] in sr:
                    sr[s["name"]]["count"] += s["count"]
                else:
                    sr[s["name"]] = s.copy()
                    service_summary += [sr[s["name"]]]
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
        # Build result
        r = {
            "id": self.object.id,
            "object": self.object,
            "name": self.object.name,
            "address": self.object.address,
            "platform": self.object.platform or "Unknown",
            "version": self.object.version.version,
            "description": self.object.description,
            "object_profile": self.object.object_profile.id,
            "object_profile_name": self.object.object_profile.name,
            "macs": ", ".join(sorted(macs)),
            "segment": self.object.segment,
            "recommended_version": "X.Y.Z",
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
            "interfaces": interfaces
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
