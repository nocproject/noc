# ---------------------------------------------------------------------
# ManagedObject card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import operator
from collections import defaultdict

# Third-party modules
from django.db.models import Q
from mongoengine.errors import DoesNotExist

# NOC modules
from .base import BaseCard
from noc.sa.models.managedobject import ManagedObject, ManagedObjectAttribute
from noc.sa.models.servicesummary import SummaryItem
from noc.sa.models.service import Service
from noc.sa.models.servicesummary import ServiceSummary
from noc.sa.models.useraccess import UserAccess
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.uptime import Uptime
from noc.inv.models.object import Object
from noc.inv.models.resourcegroup import ResourceGroup
from noc.inv.models.discoveryid import DiscoveryID
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from noc.inv.models.firmwarepolicy import FirmwarePolicy
from noc.inv.models.sensor import Sensor
from noc.maintenance.models.maintenance import Maintenance
from noc.core.text import alnum_key, list_to_ranges
from noc.core.pm.utils import MetricProxy
from noc.core.perf import metrics


class ManagedObjectCard(BaseCard):
    name = "managedobject"
    default_template_name = "managedobject"
    model = ManagedObject

    def get_object(self, id):
        if self.current_user.is_superuser:
            return ManagedObject.objects.get(id=id)
        else:
            return ManagedObject.objects.get(
                id=id, administrative_domain__in=self.get_user_domains()
            )

    def get_template_name(self):
        return self.object.object_profile.card or "managedobject"

    # get data function
    def get_data(self):

        def sortdict(dct):
            kys = sorted(dct.keys())
            res = {}
            for x in kys:
                for k, v in dct.items():
                    if k == x:
                        res[k] = v
            return res

        def get_container_path(self):
            # Get container path
            if not self.object:
                return None
            cp = []
            if self.object.container:
                c = self.object.container.id
                while c:
                    try:
                        o = Object.objects.get(id=c)
                        # @todo: Address data
                        if o.container:
                            cp.insert(0, {"id": o.id, "name": o.name})
                        c = o.container.id if o.container else None
                    except DoesNotExist:
                        metrics["error", ("type", "no_such_object")] += 1
                        break
            return cp

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
        if self.object.is_managed:
            if self.object.get_status():
                if alarms:
                    current_state = "alarm"
                else:
                    current_state = "up"
                uptime = Uptime.objects.filter(object=self.object.id, stop=None).first()
                if uptime:
                    current_start = uptime.start
            else:
                current_state = "down"
                _, current_start = self.object.get_last_status()
        else:
            current_state = "unmanaged"
        if current_start:
            duration = now - current_start

        cp = get_container_path(self)

        # MAC addresses
        macs = []
        o_macs = DiscoveryID.macs_for_object(self.object)
        for f, l in o_macs:
            if f == l:
                macs += [f]
            else:
                macs += [f"{f} - {l}"]
        # Hostname
        hostname = ""
        did = DiscoveryID.objects.filter(object=self.object.id).first()
        if did and did.hostname:
            hostname = did.hostname
        # Links
        uplinks = set(self.object.uplinks)
        if len(uplinks) > 1:
            if self.object.segment.lost_redundancy:
                redundancy = "L"
            else:
                redundancy = "R"
        else:
            redundancy = "N"
        links = []
        for _link in Link.object_links(self.object):
            local_interfaces = []
            remote_interfaces = []
            remote_objects = set()
            for iface in _link.interfaces:
                if iface.managed_object.id == self.object.id:
                    local_interfaces += [iface]
                else:
                    remote_interfaces += [iface]
                    remote_objects.add(iface.managed_object)
            if len(remote_objects) == 1:
                ro = remote_objects.pop()
                if ro.id in uplinks:
                    role = "uplink"
                else:
                    role = "downlink"
                links += [
                    {
                        "id": _link.id,
                        "role": role,
                        "local_interface": sorted(
                            local_interfaces, key=lambda x: alnum_key(x.name)
                        ),
                        "remote_object": ro,
                        "remote_interface": sorted(
                            remote_interfaces, key=lambda x: alnum_key(x.name)
                        ),
                        "remote_status": "up" if ro.get_status() else "down",
                    }
                ]
            links = sorted(
                links,
                key=lambda x: (x["role"] != "uplink", alnum_key(x["local_interface"][0].name)),
            )
        # Build global services summary
        service_summary = ServiceSummary.get_object_summary(self.object)
        # Metrics
        metric_proxy = MetricProxy(managed_object=self.object.bi_id)
        # Object Metrics
        data = defaultdict(list)
        for v_scope in metric_proxy.iter_object_metrics():
            for field, v in v_scope.items():
                data[v.value_type.name].append(
                    {
                        "name": v.humanize_meta or v.value_type.name,  # Metric Type + Meta
                        "type": v.value_units.label if v.value_units != "Scalar" else "",
                        "value": v.humanize(),
                        "threshold": None,
                    }
                )
        o_metrics = []
        for k, values in data.items():
            collapsed = len(values) == 1
            is_danger = False
            for vv in values:
                if vv["threshold"]:
                    is_danger |= True
                    collapsed |= True
            o_metrics.append(
                {"name": k, "value": values, "collapsed": collapsed, "is_danger": is_danger}
            )
        sensors = list(Sensor.objects.filter(managed_object=self.object.id).order_by("label"))
        s_meta = []
        if sensors:
            sensor_proxy = MetricProxy(sensor__in=[x.bi_id for x in sensors])
            # Sensors Metrics
            for s in sensors:
                value = sensor_proxy.sensor.value.status.value(sensor=s.bi_id)
                # sensors[s.label].append(
                #     {
                #         "name": s.label,
                #         "type": s.units.label,
                #         "value": value,
                #         "threshold": None,
                #     }
                # )
                s_meta.append(
                    {
                        "name": s.label,
                        "value": {
                            "name": s.label,
                            "type": s.units.label,
                            "value": value,
                            "threshold": None,
                        },
                        "is_danger": False,
                    }
                )
        # Interfaces
        interfaces = []
        for i in Interface.objects.filter(managed_object=self.object.id, type="physical"):
            interfaces += [
                {
                    "id": i.id,
                    "name": i.name,
                    "admin_status": i.admin_status,
                    "oper_status": i.oper_status,
                    "mac": i.mac or "",
                    "full_duplex": i.full_duplex,
                    "speed": max([i.in_speed or 0, i.out_speed or 0]) / 1000,
                    "untagged_vlan": None,
                    "tagged_vlan": None,
                    "profile": i.profile,
                    "service": i.service,
                    "service_summary": service_summary.get("interface").get(i.id, {}),
                    "description": i.description,
                }
            ]
            si = list(i.subinterface_set.filter(enabled_afi="BRIDGE"))
            if len(si) == 1:
                si = si[0]
                interfaces[-1]["untagged_vlan"] = si.untagged_vlan
                interfaces[-1]["tagged_vlans"] = list_to_ranges(si.tagged_vlans).replace(",", ", ")
        interfaces = sorted(interfaces, key=lambda x: alnum_key(x["name"]))
        # Resource groups
        # Service groups (i.e. server)
        static_services = set(self.object.static_service_groups)
        service_groups = []
        for rg_id in self.object.effective_service_groups:
            rg = ResourceGroup.get_by_id(rg_id)
            if rg:
                service_groups += [
                    {
                        "id": rg_id,
                        "name": rg.name,
                        "technology": rg.technology,
                        "is_static": rg_id in static_services,
                    }
                ]
        # Client groups (i.e. client)
        static_clients = set(self.object.static_client_groups)
        client_groups = []
        for rg_id in self.object.effective_client_groups:
            rg = ResourceGroup.get_by_id(rg_id)
            if rg:
                client_groups += [
                    {
                        "id": rg_id,
                        "name": rg.name,
                        "technology": rg.technology,
                        "is_static": rg_id in static_clients,
                    }
                ]
        # @todo: Administrative domain path
        # Alarms
        alarm_list = []
        for a in alarms:
            alarm_list += [
                {
                    "id": a.id,
                    "root_id": self.get_root(alarms),
                    "timestamp": a.timestamp,
                    "duration": now - a.timestamp,
                    "subject": a.subject,
                    "managed_object": a.managed_object,
                    "service_summary": {
                        "service": SummaryItem.items_to_dict(a.total_services),
                        "subscriber": SummaryItem.items_to_dict(a.total_subscribers),
                    },
                    "alarm_class": a.alarm_class,
                }
            ]
        alarm_list = sorted(alarm_list, key=operator.itemgetter("timestamp"))

        # Maintenance
        maintenance = []
        m_id = [am_id for am_id in self.object.affected_maintenances]
        for m in Maintenance.objects.filter(
            id__in=m_id, is_completed=False, start__lte=now + datetime.timedelta(hours=1)
        ):
            maintenance += [
                {
                    "maintenance": m,
                    "id": m.id,
                    "subject": m.subject,
                    "start": m.start,
                    "stop": m.stop,
                    "in_progress": m.start <= now,
                }
            ]
        # Get Inventory
        inv = []
        for p in self.object.get_inventory():
            c = self.get_nested_inventory(p)
            c["name"] = p.name or self.object.name
            inv += [c]
        # Build result

        if self.object.platform is not None:
            platform = self.object.platform.name
        else:
            platform = "Unknown"
        if self.object.version is not None:
            version = self.object.version.version
        else:
            version = ""
        # Diagnostics
        diagnostics = []
        for d in sorted(self.object.diagnostic, key=lambda x: x.config.display_order):
            if not d.config.show_in_display:
                continue
            diagnostics.append(
                {
                    "name": d.diagnostic[:6],
                    "description": d.config.display_description,
                    "state": d.state.value,
                    "state__label": d.state.value,
                    "details": [
                        {
                            "name": c.name,
                            "state": {True: "OK", False: "Error"}[c.status],
                            "error": c.error,
                        }
                        for c in d.checks or []
                    ],
                    "reason": d.reason or "",
                }
            )
        mp = MetricProxy(managed_object=self.object.bi_id)
        r = {
            "id": self.object.id,
            "object": self.object,
            "name": self.object.name,
            "address": self.object.address,
            "platform": platform,
            # self.object.platform.name if self.object.platform else "Unknown",
            "version": version,
            # self.object.version.version if self.object.version else "",
            "description": self.object.description,
            "object_profile": self.object.object_profile.id,
            "object_profile_name": self.object.object_profile.name,
            "metric_proxy": mp,
            "iface_metrics": mp.interface(
                group_by=["interface", "managed_object"],
                queries=["load_in", "load_out", "errors_in", "errors_out"],
            ),
            "hostname": hostname,
            "macs": ", ".join(sorted(macs)),
            "segment": self.object.segment,
            "firmware_status": FirmwarePolicy.get_status(self.object.version, self.object.platform),
            "firmware_recommended": FirmwarePolicy.get_recommended_version(self.object.platform),
            "service_summary": service_summary,
            "container_path": cp,
            "current_state": current_state,
            # Start of uptime/downtime
            "current_start": current_start,
            # Current uptime/downtime
            "current_duration": duration,
            "service_groups": service_groups,
            "client_groups": client_groups,
            "tt": [],
            "links": links,
            "alarms": alarm_list,
            "interfaces": interfaces,
            "metrics": o_metrics,
            "sensors": s_meta,
            "maintenance": maintenance,
            "redundancy": redundancy,
            "inventory": self.flatten_inventory(inv),
            "serial_number": self.object.get_attr("Serial Number"),
            "attributes": list(
                ManagedObjectAttribute.objects.filter(managed_object=self.object.id)
            ),
            "diagnostics": diagnostics,
            "confdb": None,
        }
        try:
            r["confdb"] = self.object.get_confdb()
        except (SyntaxError, ValueError):
            pass
        return r

    def get_service_glyphs(self, service):
        """
        Returns a list of (service profile name, glyph)
        """
        r = []
        if service.state.name in ("Testing", "Ready", "Suspended"):
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
            r += [
                {
                    "scope": "managedobject",
                    "id": mo.id,
                    "label": "%s (%s) [%s]" % (mo.name, mo.address, mo.platform),
                }
            ]
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
            "children": [],
        }
        if_map = {c.name: c.interface_name for c in o.connections}
        for n in o.model.connections:
            if n.direction == "i":
                c, r_object, _ = o.get_p2p_connection(n.name)
                if c is None:
                    r["children"] += [
                        {
                            "id": "",
                            "name": n.name,
                            "serial": "",
                            "description": "--- EMPTY ---",
                            "model": "",
                            "interface": if_map.get(n.name) or "",
                        }
                    ]
                else:
                    cc = self.get_nested_inventory(r_object)
                    cc["name"] = n.name
                    cc["interface"] = if_map.get(n.name) or ""
                    r["children"] += [cc]
            elif n.direction == "s":
                r["children"] += [
                    {
                        "id": "",
                        "name": n.name,
                        "serial": "",
                        "description": n.description,
                        "model": ", ".join(str(p) for p in n.protocols),
                        "interface": if_map.get(n.name) or "",
                    }
                ]
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

    @staticmethod
    def get_root(_root):
        for value in _root:
            if value.root is not None:
                return value.root
