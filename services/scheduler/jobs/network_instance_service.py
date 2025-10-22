# ----------------------------------------------------------------------
# ETL Sync Job Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Dict, Optional, Tuple, List, Any

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
from noc.inv.models.subinterface import SubInterface

# bitTest(mac, 41) filter locally administered
# AND NOT bitTest(mac, 41)
SQL = """
SELECT managed_object, interface, groupUniqArray(MACNumToString(mac)) as u_macs,
   argMax(vlan, last_seen) as vlan, argMax(last_seen, last_seen) as ls, COUNT(DISTINCT mac) as macs_cnt
 FROM noc.macdb
 WHERE toDate(last_seen) > %s
 GROUP BY managed_object, interface
 HAVING macs_cnt < %s
 ORDER BY managed_object
 FORMAT JSON
"""

REQUEST_DAYS = 7
LIMIT_MAC_BY_PORT = 70
CHUNK = 2000


class NetworkInstanceDiscoveryJob(PeriodicJob):
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
            return
        bulk = []
        processed, objects = set(), set()
        # Processed Instances
        for svc, refs in ServiceInstance.objects.filter(
            type=InstanceType.ASSET, asset_refs__in=list(mac_iface_map)
        ).scalar("service", "asset_refs"):
            updates = len(bulk)
            ifaces, update_ts = [], None
            for mac_ref in refs:
                if mac_ref not in mac_iface_map:
                    continue
                iface, update_ts = mac_iface_map[mac_ref]
                ifaces.append(iface)
            if ifaces:
                si = svc.register_instance(
                    InstanceType.NETWORK_CHANNEL,
                    source=InputSource.DISCOVERY,
                    managed_object=ifaces[0].managed_object,
                )
                si.update_resources(
                    ifaces, source=InputSource.DISCOVERY, update_ts=update_ts, bulk=bulk
                )
                processed.add(svc.id)
                if len(bulk) != updates:
                    self.logger.info("[%s] Bind to interface: %s", svc, ifaces)
                    objects |= {i.managed_object for i in ifaces}
                for r in refs:
                    # Exclude duplicate
                    mac_iface_map.pop(r, None)
        asset_services = list(
            ServiceInstance.objects.filter(
                type=InstanceType.ASSET,
                service__nin=list(processed),
                asset_refs__exists=True,
            ).scalar("service")
        )
        # Removed All resources with Manual... ?
        # TTL last_seen/Move MAC
        for si in ServiceInstance.objects.filter(
            type=InstanceType.NETWORK_CHANNEL,
            sources=InputSource.DISCOVERY,
            service__in=asset_services,
        ):
            self.logger.debug("[%s] UnBind from interface, ", si)
            # TTL Removed
            si.unseen(source=InputSource.DISCOVERY)
            # MAC Moved
            # si.update_resources([], source=InputSource.DISCOVERY)
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
    def processed_records(
        cls, rows: List[Dict[str, Any]]
    ) -> Dict[str, Tuple[Interface, datetime.datetime]]:
        """"""
        r = {}
        ref = ValueType.MAC_ADDRESS
        mos_id_map = dict(
            ManagedObject.objects.filter(
                bi_id__in=[int(x["managed_object"]) for x in rows]
            ).values_list("bi_id", "id"),
        )
        # Filter Tagged ports
        tagged_si = {
            s["interface"]
            for s in SubInterface.objects.filter(
                enabled_afi="BRIDGE",
                tagged_vlans__exists=True,
                tagged_vlans__ne=[],
                managed_object__in=list(mos_id_map.values()),
            )
            .scalar("interface")
            .as_pymongo()
        }
        # Find Interface
        interfaces = {}
        for iface in Interface.objects.filter(
            managed_object__in=list(mos_id_map.values()), type="physical"
        ):
            if iface.id in tagged_si:
                # Filter Trunked ports
                continue
            interfaces[iface.managed_object.bi_id, iface.name] = iface
        for row in rows:
            if int(row["managed_object"]) not in mos_id_map:
                # Unknown ManagedObject
                continue
            iface = interfaces.get((int(row["managed_object"]), row["interface"]))
            if not iface:
                continue
            for m in row["u_macs"]:
                # Getting MAC Refs
                r[ref.clean_reference(m)] = (
                    iface,
                    datetime.datetime.fromisoformat(row["ls"]),
                )
        return r

    @classmethod
    def get_mac_neighbors(
        cls, start: Optional[datetime.datetime] = None, limit_mac_by_port: Optional[int] = None
    ) -> Dict[str, Tuple[Interface, datetime.datetime]]:
        """Return Iface -> Mac Neighbor map"""
        limit_mac_by_port = limit_mac_by_port or LIMIT_MAC_BY_PORT
        start = start or (datetime.datetime.now() - datetime.timedelta(days=REQUEST_DAYS))
        ch = connection()
        r = ch.execute(SQL, args=[start.date().isoformat(), limit_mac_by_port], return_raw=True)
        r = orjson.loads(r)
        mac_iface_map, rows = {}, []
        for row in r["data"]:
            rows.append(row)
            if len(rows) > CHUNK:
                mac_iface_map |= cls.processed_records(rows)
                rows = []
        # Processed Administrative-local-address
        if rows:
            mac_iface_map |= cls.processed_records(rows)
        return mac_iface_map
