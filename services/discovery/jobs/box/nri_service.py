# ----------------------------------------------------------------------
# Service Mapper check
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict

# Third-party modules
from typing import Dict, List, Any, DefaultDict

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.sa.models.serviceinstance import ServiceInstance
from noc.sa.models.servicesummary import ServiceSummary
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface
from noc.core.change.policy import change_tracker
from noc.core.models.inputsources import InputSource
from noc.core.ip import IP


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
        profiles = {}
        resources: DefaultDict[ServiceInstance, List[Any]] = defaultdict(list)
        # Managed Object Binding
        for si in ServiceInstance.iter_object_instances(self.object):
            if si.service.profile.instance_policy == "D":
                # Disabled resource binding
                continue
            if not si.managed_object or si.managed_object != self.object:
                self.logger.info("Bind object to Service Instance: %s", si)
                si.refresh_managed_object(self.object)
            processed_instances[si.id] = si
        # For ManagedObject not in SI - Reset
        for si in ServiceInstance.objects.filter(
            managed_object=self.object,
            id__nin=list(processed_instances),
            sources__in=[InputSource.ETL, InputSource.CONFIG],
        ):
            si.reset_object()
            self.logger.info("UnBind object to Service Instance: %s", si)
        bulk = []
        # Extract ResourceKey
        # resource_key -> ServiceInstance
        nri_map_instances: Dict[str, ServiceInstance] = {}
        address_map_instance: Dict[str, ServiceInstance] = {}
        for si in ServiceInstance.objects.filter(
            managed_object=self.object,
            sources__in=[InputSource.ETL, InputSource.CONFIG],
        ):
            if si.service.profile.instance_policy == "D":
                # Disabled resource binding
                # Unbind
                continue
            # Local Binding
            if si.nri_port:
                nri_map_instances[si.nri_port] = si
            if si.config.allow_resources:
                for addr in si.addresses:
                    p = IP.prefix(addr.address)
                    if p.address != self.object.address:
                        continue
                    address_map_instance[p.address] = si
        # Resolve resources by key
        if nri_map_instances:
            self.map_nri_ports(nri_map_instances, resources, profiles)
        if address_map_instance:
            self.map_address_port(address_map_instance, resources, profiles)
        if not resources and not processed_instances:
            self.logger.info("Nothing resource for updated")
            return
        # Refresh resources
        for si, rs in resources.items():
            si.update_resources(rs, source=InputSource.CONFIG, bulk=bulk)
        for si in set(processed_instances) - {x.id for x in resources}:
            processed_instances[si].update_resources([], source=InputSource.CONFIG, bulk=bulk)
        for iface, profile in profiles.items():
            if iface.profile != profile:
                self.logger.info("[%s] Set profile from service: %s", iface, profile)
                iface.profile = profile
                iface.save()
        if bulk:
            si_col = ServiceInstance._get_collection()
            self.logger.info("Sending %d updates", len(bulk))
            self.logger.debug("Sending updates: %s", bulk)
            si_col.bulk_write(bulk, ordered=True)
            ServiceSummary.refresh_object(self.object.id)
            change_tracker.register("update", "sa.ManagedObject", str(self.object.id), [])

    def map_nri_ports(
        self,
        instances: Dict[str, ServiceInstance],
        resources: Dict[ServiceInstance, List[Any]],
        profiles: Dict[Any, Interface],
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
            if instances[iface.nri_name].service.profile.interface_profile:
                profiles[iface] = instances[iface.nri_name].service.profile.interface_profile

    def map_address_port(
        self,
        addresses: Dict[str, ServiceInstance],
        resources: Dict[ServiceInstance, List[Any]],
        profiles: Dict[Any, Interface],
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
                if (
                    si.name == si.interface.name
                    or si.name in self.object.get_profile().get_interface_names(si.name)
                ):
                    resources[addresses[addr.address]] += [si.interface]
                else:
                    resources[addresses[addr.address]] += [si]
                if addresses[addr.address].service.profile.interface_profile:
                    profiles[si.interface] = addresses[
                        addr.address
                    ].service.profile.interface_profile
