# ----------------------------------------------------------------------
# Service Mapper check
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
import datetime

# Third-party modules
import orjson
from typing import Dict, List, Any, DefaultDict

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.sa.models.serviceinstance import ServiceInstance, DISCOVERY_SOURCE, CLIENT_INSTANCE_NAME
from noc.sa.models.servicesummary import ServiceSummary
from noc.sa.models.service import Service
from noc.sa.models.serviceprofile import ServiceProfile
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface
from noc.core.change.policy import change_tracker
from noc.core.clickhouse.connect import connection
from noc.core.ip import IP


SQL = """
SELECT interface, groupUniqArray(MACNumToString(if_mac)) as macs, COUNT(DISTINCT if_mac) as macs_cnt
  FROM (
    SELECT interface, argMax(mac, ts) as if_mac
    FROM mac WHERE date >= %s AND managed_object = %s
    GROUP BY interface, mac
  )
  GROUP BY interface
  HAVING macs_cnt < 3
  FORMAT JSON
"""


class NRIServiceCheck(DiscoveryCheck):
    """
    Network Resource Inventory service mapper
    Maps NRI service to local interface
    Create ServiceInstance by Static instance rules
    """

    name = "nri_service"

    def handler(self):
        self.logger.info("NRI Service Mapper")
        processed_instances = {}
        resources: DefaultDict[ServiceInstance, List[Any]] = defaultdict(list)
        # Managed Object Binding
        for si in ServiceInstance.iter_object_instances(self.object):
            if si.service.profile.instance_policy == "D":
                # Disabled resource binding
                continue
            if not si.managed_object or si.managed_object != self.object:
                self.logger.info("Bind object to Service Instance: %s", si)
                si.set_object(self.object)
            si.seen(DISCOVERY_SOURCE)
            processed_instances[si.id] = si
        # New Instances
        global_iface_map_instances = self.get_remote_resource_svcs()
        for svc, iface in global_iface_map_instances.items():
            si = svc.register_instance(
                DISCOVERY_SOURCE,
                port=0,
                name=CLIENT_INSTANCE_NAME,
                managed_object=self.object,
            )
            processed_instances[si.id] = si
            resources[si].append(iface)
        # unseen
        for si in ServiceInstance.objects.filter(
            managed_object=self.object,
            id__nin=list(processed_instances),
            sources__in=[DISCOVERY_SOURCE],
        ):
            si.reset_object()
            si.unseen(DISCOVERY_SOURCE)
            self.logger.info("UnBind object to Service Instance: %s", si)
        bulk = []
        # Extract ResourceKey
        # resource_key -> ServiceInstance
        nri_map_instances: Dict[str, ServiceInstance] = {}
        address_map_instance: Dict[str, ServiceInstance] = {}
        for si in ServiceInstance.objects.filter(managed_object=self.object):
            if si.service.profile.instance_policy == "D":
                # Disabled resource binding
                continue
            ss = si.get_instance_settings()
            # Local Binding
            if si.nri_port:
                nri_map_instances[si.nri_port] = si
            if ss.allow_resources:
                for addr in si.addresses:
                    p = IP.prefix(addr.address)
                    address_map_instance[p.address] = si
        # Resolve resources by key
        if nri_map_instances:
            self.map_nri_ports(nri_map_instances, resources)
        if address_map_instance:
            self.map_address_port(address_map_instance, resources)
        if not resources:
            self.logger.info("Nothing resource for updated")
            return
        # Refresh resources
        for si, rs in resources.items():
            si.update_resources(rs, source=DISCOVERY_SOURCE, bulk=bulk)
        for si in set(processed_instances) - {x.id for x in resources}:
            processed_instances[si].update_resources([], source=DISCOVERY_SOURCE, bulk=bulk)
        if bulk:
            si_col = ServiceInstance._get_collection()
            self.logger.info("Sending %d updates", len(bulk))
            self.logger.debug("Sending updates: %s", bulk)
            si_col.bulk_write(bulk, ordered=True)
            ServiceSummary.refresh_object(self.object.id)
            change_tracker.register("update", "sa.ManagedObject", str(self.object.id), [])

    def map_nri_ports(
        self, instances: Dict[str, ServiceInstance], resources: Dict[ServiceInstance, List[Any]]
    ):
        """Resolve Resource by nri_name"""
        # Check object has interfaces
        if not self.has_capability("DB | Interfaces"):
            self.logger.info("No interfaces discovered. Skipping NRI Portmap")
            return
        for iface in Interface.objects.filter(managed_object=self.object.id, nri_name__exists=True):
            if not iface.nri_name or iface.nri_name not in instances:
                continue
            resources[instances[iface.nri_name]] += [iface]

    def map_address_port(
        self,
        addresses: Dict[str, ServiceInstance],
        resources: Dict[ServiceInstance, List[Any]],
    ):
        """Resolve Resource by IP Address"""
        if not self.has_capability("DB | Interfaces"):
            self.logger.info("No interfaces discovered. Skipping Addresses Portmap")
            return
        for si in SubInterface.objects.filter(
            managed_object=self.object.id, ipv4_addresses__exists=True
        ):
            for addr in si.ipv4_addresses:
                addr = IP.prefix(addr)
                if addr.address not in addresses:
                    continue
                resources[addresses[addr.address]] += [si]

    def get_mac_neighbors(self) -> Dict[str, Interface]:
        """Return Iface -> Mac Neighbor map"""
        now = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
        ch = connection()
        r = ch.execute(SQL, args=[now.isoformat(), self.object.bi_id], return_raw=True)
        r = orjson.loads(r)
        mac_iface_map = {}
        for row in r["data"]:
            for m in row["macs"]:
                iface = self.object.get_interface(row["interface"])
                if not iface:
                    continue
                mac_iface_map[m] = iface
        return mac_iface_map

    def get_remote_resource_svcs(self) -> Dict[Service, Interface]:
        """Mapping Remote Resource to Service"""
        if not self.has_capability("DB | Interfaces"):
            self.logger.info("No interfaces discovered. Skipping Remote Portmap")
            return {}
        elif not self.object.object_profile.enable_periodic_discovery_mac:
            self.logger.info("No MAC discovered enabled. Skipping Remote Portmap")
            return {}
        remote_resource_svcs = list(
            ServiceProfile.objects.filter(
                instance_policy="O",
                instance_policy_settings__provide="C",
            ).scalar("id")
        )
        if not remote_resource_svcs:
            return {}
        # Remote By MAC
        r = {}
        mac_iface_map = self.get_mac_neighbors()
        if not mac_iface_map:
            return r
        for svc in Service.objects.filter(
            cpe_mac__in=list(mac_iface_map),
            profile__in=remote_resource_svcs,
        ):
            r[svc] = mac_iface_map[svc.cpe_mac]
        return r
