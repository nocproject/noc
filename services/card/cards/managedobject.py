# ---------------------------------------------------------------------
# ManagedObject card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import OrderedDict
import datetime
import operator

# Third-party modules
from django.db.models import Q
from mongoengine.errors import DoesNotExist

# NOC modules
from .base import BaseCard
from noc.sa.models.managedobject import ManagedObject, ManagedObjectAttribute
from noc.fm.models.activealarm import ActiveAlarm
from noc.sa.models.servicesummary import SummaryItem
from noc.fm.models.uptime import Uptime
from noc.inv.models.object import Object
from noc.inv.models.resourcegroup import ResourceGroup
from noc.inv.models.discoveryid import DiscoveryID
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from noc.sa.models.service import Service
from noc.inv.models.firmwarepolicy import FirmwarePolicy
from noc.sa.models.servicesummary import ServiceSummary
from noc.core.text import alnum_key, list_to_ranges
from noc.maintenance.models.maintenance import Maintenance
from noc.pm.models.thresholdprofile import ThresholdProfile
from noc.sa.models.useraccess import UserAccess
from noc.core.pm.utils import get_interface_metrics, get_objects_metrics, get_dict_interface_metrics
from noc.pm.models.metrictype import MetricType
from noc.pm.models.metricscope import MetricScope
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

    def get_threshold_config(self, threshold_profile, w_value):
        """
        :param threshold_profile:
        :type threshold_profile: ThresholdProfile
        :param w_value: Window value
        :type w_value: int
        :return:
        :rtype:
        """
        for threshold in threshold_profile.thresholds:
            if threshold.is_open_match(w_value):
                return True
            if threshold.is_clear_match(w_value):
                return False
        return False

    # get data function
    def get_data(self):
        intervals = (
            ("y", 31557617),  # 60 * 60 * 24 * 7 * 52
            ("w", 604800),  # 60 * 60 * 24 * 7
            ("d", 86400),  # 60 * 60 * 24
            ("h", 3600),  # 60 * 60
            ("m", 60),
            ("s", 1),
        )

        def display_time(seconds):
            result = []

            for name, count in intervals:
                value = seconds // count
                if value:
                    seconds -= value * count
                    if value == 1:
                        name = name.rstrip("s")
                    result.append("{}{}".format(value, name))
            return ", ".join(result[:-1])

        def sortdict(dct):
            kys = sorted(dct.keys())
            res = OrderedDict()
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
        if o_macs:
            for f, l in o_macs:
                if f == l:
                    macs += [f]
                else:
                    macs += ["%s - %s" % (f, l)]
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

        # Interfaces
        interfaces = []

        mo = ManagedObject.objects.filter(id=self.object.id)
        mo = mo[0]
        meric_map = get_dict_interface_metrics(mo).get(mo)
        meric_map_revert = {v: k for k, v in meric_map.get("map").items()}
        ifaces_metrics, last_ts = get_interface_metrics(mo, meric_map)
        ifaces_metrics = ifaces_metrics[mo]

        objects_metrics, last_time = get_objects_metrics(mo)
        objects_metrics = objects_metrics.get(mo)

        # Sensors
        sensors_metrics = None
        s_metrics = None
        sensors = {}
        s_meta = []
        STATUS = {0: "OK", 1: "Alarm"}
        meric_map = {}
        if mo.get_caps().get("Sensor | Controller"):
            for mc in MetricType.objects.filter(scope=MetricScope.objects.get(name="Environment")):
                if meric_map:
                    meric_map["map"].update({mc.field_name: mc.name})
                else:
                    meric_map = {"table_name": mc.scope.table_name, "map": {mc.field_name: mc.name}}
            sensors_metrics, last_ts = get_interface_metrics(mo, meric_map)
            sensors_metrics = sensors_metrics[mo]

        m_tp = {}
        if mo.object_profile.metrics:
            for mt in mo.object_profile.metrics:
                if mt.get("threshold_profile"):
                    threshold_profile = ThresholdProfile.get_by_id(mt.get("threshold_profile"))
                    m_tp[MetricType.get_by_id(mt.get("metric_type")).name] = threshold_profile
        data = {}
        meta = []
        metric_type_name = {x.name: x.units.label for x in MetricType.objects.filter()}
        metric_type_field = {x.field_name: x.units.label for x in MetricType.objects.filter()}
        if objects_metrics:
            for path, mres in objects_metrics.items():
                t_v = False
                for key in mres:
                    m_path = path if any(path.split("|")) else key
                    m_path = " | ".join(kk.strip() for kk in m_path.split("|"))
                    if m_tp.get(key):
                        t_v = self.get_threshold_config(m_tp.get(key), int(mres[key]))
                    val = {
                        "name": m_path,
                        "type": "" if m_path == "Object | SysUptime" else metric_type_name[key],
                        "value": (
                            display_time(int(mres[key]))
                            if m_path == "Object | SysUptime"
                            else mres[key]
                        ),
                        "threshold": t_v,
                    }
                    if data.get(key):
                        data[key] += [val]
                    else:
                        data[key] = [val]

        data = sortdict(data)
        for k, d in data.items():
            collapsed = False
            if len(d) == 1:
                collapsed = True
            for dd in d:
                isdanger = False
                if dd["threshold"]:
                    isdanger = True
                    collapsed = True
            meta.append({"name": k, "value": d, "collapsed": collapsed, "isdanger": isdanger})

        for i in Interface.objects.filter(managed_object=self.object.id, type="physical"):
            load_in = "-"
            load_out = "-"
            iface_metrics = ifaces_metrics.get(str(i.name))
            interface_metrics = {}
            if iface_metrics:
                for key, value in iface_metrics.items():
                    metric_type = metric_type_name.get(key) or metric_type_field.get(key)
                    if key == "Interface | Load | In":
                        load_in = (
                            "%s%s" % (self.humanize_speed(value, metric_type), metric_type)
                            if value
                            else "-"
                        )
                    if key == "Interface | Load | Out":
                        load_out = (
                            "%s%s" % (self.humanize_speed(value, metric_type), metric_type)
                            if value
                            else "-"
                        )
                    try:
                        interface_metrics[meric_map_revert[key]] = value if value else "-"
                    except KeyError:
                        pass
            interfaces += [
                {
                    "id": i.id,
                    "name": i.name,
                    "admin_status": i.admin_status,
                    "oper_status": i.oper_status,
                    "mac": i.mac or "",
                    "full_duplex": i.full_duplex,
                    "load_in": load_in,
                    "load_out": load_out,
                    "speed": max([i.in_speed or 0, i.out_speed or 0]) / 1000,
                    "untagged_vlan": None,
                    "tagged_vlan": None,
                    "profile": i.profile,
                    "service": i.service,
                    "service_summary": service_summary.get("interface").get(i.id, {}),
                    "description": i.description,
                    "metrics": interface_metrics,
                }
            ]
            if sensors_metrics:
                s_metrics = sensors_metrics.get(str(i.name))
            if s_metrics:
                sens_metrics = []
                for i_metrics in i.profile.metrics:
                    sens_metrics.append(i_metrics.metric_type.name)
                for key, value in s_metrics.items():
                    if key not in sens_metrics:
                        continue
                    val = {
                        "name": key,
                        "type": metric_type_name[key],
                        "value": STATUS.get(value) if metric_type_name[key] == " " else value,
                        "threshold": None,
                    }
                    if sensors.get(i.name):
                        sensors[i.name] += [val]
                    else:
                        sensors[i.name] = [val]

            si = list(i.subinterface_set.filter(enabled_afi="BRIDGE"))
            if len(si) == 1:
                si = si[0]
                interfaces[-1]["untagged_vlan"] = si.untagged_vlan
                interfaces[-1]["tagged_vlans"] = list_to_ranges(si.tagged_vlans).replace(",", ", ")

        if sensors:
            sensors = sortdict(sensors)
            for k, d in sensors.items():
                for dd in d:
                    isdanger = False
                    if dd["threshold"]:
                        isdanger = True
                s_meta.append({"name": k, "value": d, "isdanger": isdanger})

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
            "metrics": meta,
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
    def humanize_speed(speed, type_speed):
        def func_to_bytes(speed):
            try:
                speed = float(speed)
            except ValueError:
                pass
                # speed = speed / 8.0
            if speed < 1024:
                return speed
            for t, n in [(pow(2, 30), "G"), (pow(2, 20), "M"), (pow(2, 10), "k")]:
                if speed >= t:
                    if speed // t * t == speed:
                        return "%d% s" % (speed // t, n)
                    else:
                        return "%.2f %s" % (float(speed) / t, n)

        def func_to_bit(speed):
            if not speed:
                return "-"
            try:
                speed = int(speed)
            except ValueError:
                pass
            if speed < 1000 and speed > 0:
                return "%s " % speed
            for t, n in [(1000000000, "G"), (1000000, "M"), (1000, "k")]:
                if speed >= t:
                    if speed // t * t == speed:
                        return "%d&nbsp;%s" % (speed // t, n)
                    else:
                        return "%.2f&nbsp;%s" % (float(speed) / t, n)

        def func_to_bool(speed):
            return bool(speed)

        result = speed
        if not speed:
            result = "-"
        try:
            speed = int(speed)
        except ValueError:
            pass
        if type_speed == "bit/s":
            result = func_to_bit(speed)
        if type_speed == "bytes":
            result = func_to_bytes(speed)
        if type_speed == "bool":
            result = func_to_bool(speed)
        if result == speed:
            result = speed
        return result

    @staticmethod
    def get_root(_root):
        for value in _root:
            if value.root is not None:
                return value.root
