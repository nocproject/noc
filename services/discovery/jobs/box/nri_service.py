# ----------------------------------------------------------------------
# Service Mapper check
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from typing import Dict

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.sa.models.serviceinstance import ServiceInstance
from noc.sa.models.servicesummary import ServiceSummary
from noc.inv.models.interface import Interface
from noc.core.change.policy import change_tracker


class NRIServiceCheck(DiscoveryCheck):
    """
    Network Resource Inventory service mapper
    Maps NRI service to local interface
    Create ServiceInstance by Static instance rules
    """

    name = "nri_service"

    def handler(self):
        self.logger.info("NRI Service Mapper")
        bulk = []
        si_col = ServiceInstance._get_collection()
        nri_map_instances = {}
        # Update ServiceInstance
        for si in ServiceInstance.iter_object_instances(self.object):
            if not si.managed_object:
                si.set_object(self.object, bulk=bulk)
            if si.nri_port:
                nri_map_instances[si.nri_port] = si
            si.seen("discovery")
        # Refresh resources
        if nri_map_instances:
            self.map_nri_ports(nri_map_instances, bulk)
        if bulk:
            self.logger.info("Sending %d updates", len(bulk))
            self.logger.debug("Sending updates: %s", bulk)
            si_col.bulk_write(bulk, ordered=True)
            ServiceSummary.refresh_object(self.object.id)
            change_tracker.register("update", "sa.ManagedObject", str(self.object.id), [])

    def map_nri_ports(self, instances: Dict[str, ServiceInstance], bulk):
        # Check object has interfaces
        if not self.has_capability("DB | Interfaces"):
            self.logger.info("No interfaces discovered. Skipping NRI Portmap")
            return
        for iface in Interface.objects.filter(managed_object=self.object.id, nri_name__exists=True):
            if not iface.nri_name or iface.nri_name not in instances:
                continue
            si = instances.pop(iface.nri_name)
            si.add_resource(iface, bulk=bulk)
            self.logger.info("Binding service %s to interface %s", si.service, iface.name)
        for n, si in instances.items():
            self.logger.info("Cannot bind service %s. Cannot find NRI interface %s", si.service, n)
            si.clean_resource("if", bulk=bulk)
