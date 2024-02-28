# ----------------------------------------------------------------------
# IPPing Address
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import List

# Third-party modules
import orjson

# NOC modules
from ..box.address import AddressCheck as BaseAddressCheck, DiscoveredAddress, SRC_PING
from noc.ip.models.prefix import Prefix
from noc.ip.models.addressprofile import AddressProfile
from noc.core.clickhouse.connect import connection
from noc.core.ip import IP, PrefixDB

ADDRESS_QUERY = """
    SELECT IPv4NumToString(ip) as address, argMax(ts, pool) as pool,
     argMax(ts, hostname) as hostname, argMax(description, ts) as description, argMax(ts, ts) as last
    FROM noc.purgatorium
    WHERE has(success_checks, 'ICMP') and date >= %s and ts > %s and source = 'network-scan'
    GROUP BY ip
    FORMAT JSONEachRow
"""
JCLS_IPPING_PREFIX = "noc.services.discovery.jobs.ipping.job.IPPingDiscoveryJob"


class AddressCheck(BaseAddressCheck):
    """ """

    do_detaching = False

    def get_addresses(self):
        # vpn_id, address => DiscoveredAddress
        addresses = {}
        addresses = self.apply_addresses(addresses, self.get_purgatorium_address())
        return addresses

    def get_purgatorium_address(self) -> List[DiscoveredAddress]:
        """
        "vpn_id", "address", "profile", "description", "source", "subinterface", "mac", "fqdn"
        :return:
        """

        profile = self.object
        if not profile:
            self.logger.info("No profile_id artefact, skipping ipping addresses")
            return []
        # enable_ip_ping_discovery
        prefixes = [(p.prefix, p.vrf.vpn_id) for p in Prefix.objects.filter(profile=profile)]
        if not prefixes:
            self.logger.info("[%s] No prefixes for IP Ping enable")
            return []
        vpn_db = PrefixDB()
        for p, vpn_id in prefixes:
            vpn_db[IP.prefix(p)] = vpn_id
        address = []
        address_profile = AddressProfile.objects.filter().first()
        now = datetime.datetime.now() - datetime.timedelta(days=7)
        ts = (profile.ip_ping_discovery_last_run or now).replace(microsecond=0)
        ch = connection()
        last_ts = ts
        r = ch.execute(ADDRESS_QUERY, args=[ts.date().isoformat(), ts.isoformat()], return_raw=True)
        for row in r.splitlines():
            row = orjson.loads(row)
            # Check address in requested prefixes
            try:
                vpn_id = vpn_db[IP.prefix(row["address"])]
            except KeyError:
                continue
            address.append(
                DiscoveredAddress(
                    vpn_id=vpn_id,
                    address=row["address"],
                    profile=address_profile,
                    source=SRC_PING,
                    description=None,
                    subinterface=None,
                    mac=None,
                    fqdn=None,
                )
            )
            last_ts = max(last_ts, datetime.datetime.fromisoformat(row["last"]))
        if last_ts != self.object.ip_ping_discovery_last_run:
            self.object.ip_ping_discovery_last_run = last_ts
            self.object.save()
        self.logger.info("[%s] Processed address: %s", self.object.id, len(address))
        return address

    def is_enabled(self):
        return True
