# ----------------------------------------------------------------------
# ETL Sync Job Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Dict, Optional, Tuple

# Third-party modules
import orjson

# NOC modules
from noc.core.scheduler.periodicjob import PeriodicJob
from noc.core.clickhouse.connect import connection
from noc.core.models.serviceinstanceconfig import InstanceType
from noc.core.models.inputsources import InputSource
from noc.core.models.valuetype import ValueType
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.serviceinstance import ServiceInstance
from noc.sa.models.servicesummary import ServiceSummary
from noc.sa.models.serviceprofile import ServiceProfile
from noc.inv.models.interface import Interface

SQL = """
SELECT managed_object, interface, groupUniqArray(MACNumToString(mac)) as u_macs,
   argMax(vlan, last_seen) as vlan, argMax(last_seen, last_seen) as ls, COUNT(DISTINCT mac) as macs_cnt
 FROM noc.macdb
 WHERE toDate(last_seen) > %s
 GROUP BY managed_object, interface
 HAVING macs_cnt < 4
 FORMAT JSON
"""

REQUEST_DAYS = 14
CHUNK = 1000


class ServiceResourceBindJob(PeriodicJob):
    def handler(self, **kwargs):
        """
        Bind MAC address values
        * Request MAC -> Interface from MACDB
        * Filter networks port (NNI)
        * Request instances
        * Update resources (by interface)
        * ? MAC Avail
        """
        self.logger.info("Run Request MAC instances")
        mac_iface_map = self.get_mac_neighbors()
        # Only Access and Chained interfaces exists, Filter DiscoveryID caches and links
        if not mac_iface_map:
            return None
        bulk = []
        processed, objects = set(), set()
        # Processed Instances
        for svc, refs in ServiceInstance.objects.filter(
            type=InstanceType.ASSET, asset_refs__in=list(mac_iface_map)
        ).scalar("service", "asset_refs"):
            for mac_ref in refs:
                if mac_ref not in mac_iface_map:
                    continue
                iface, update_ts = mac_iface_map[mac_ref]
                self.logger.debug("[%s] Bind to interface: %s", svc, iface)
                si = svc.register_instance(
                    InstanceType.NETWORK_CHANNEL, managed_object=iface.managed_object
                )
                si.update_resources(
                    [iface], source=InputSource.DISCOVERY, update_ts=update_ts, bulk=bulk
                )
                processed.add(svc.id)
                break
        asset_services = [
            svc
            for svc in ServiceInstance.objects.filter(
                type=InstanceType.ASSET,
                service__nin=list(processed),
                asset_refs__exists=True,
            ).scalar("service")
        ]
        for si in ServiceInstance.objects.filter(
            type=InstanceType.NETWORK_CHANNEL,
            service__in=asset_services,
        ):
            self.logger.debug("[%s] UnBind from interface, ", si)
            si.update_resources([], source=InputSource.DISCOVERY)
        coll = ServiceInstance._get_collection()
        self.logger.info("Updated: %s", len(bulk))
        if bulk:
            coll.bulk_write(bulk)
        for o in objects:
            ServiceSummary.refresh_object(o)

    def can_run(self):
        return bool(ServiceProfile.objects.filter(instance_policy__ne="D").first())

    def get_interval(self):
        """
        Returns next repeat interval
        """
        return 300

    @classmethod
    def get_mac_neighbors(
        cls,
        start: Optional[datetime.datetime] = None,
    ) -> Dict[str, Tuple[Interface, datetime.datetime]]:
        """Return Iface -> Mac Neighbor map"""
        now = (datetime.datetime.now() - datetime.timedelta(days=REQUEST_DAYS)).date()
        ch = connection()
        ref = ValueType.MAC_ADDRESS
        r = ch.execute(SQL, args=[now.isoformat()], return_raw=True)
        r = orjson.loads(r)
        mac_iface_map = {}
        mos_id_map = dict(
            ManagedObject.objects.filter(
                bi_id__in=[int(x["managed_object"]) for x in r["data"]]
            ).values_list("bi_id", "id"),
        )
        for row in r["data"]:
            if int(row["managed_object"]) not in mos_id_map:
                # Unknown ManagedObject
                continue
            # Check 'DB | Interfaces' if not exist - add to ignored
            iface = Interface.objects.filter(
                managed_object=mos_id_map[int(row["managed_object"])], name=row["interface"]
            ).first()
            for m in row["u_macs"]:
                # Getting MAC Refs
                mac_iface_map[ref.clean_reference(m)] = (
                    iface,
                    datetime.datetime.fromisoformat(row["ls"]),
                )
        return mac_iface_map
