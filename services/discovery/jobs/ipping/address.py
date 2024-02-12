# ----------------------------------------------------------------------
# <describe module here>
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
from ..box.address import AddressCheck as BaseAddressCheck, DiscoveredAddress, GLOBAL_VRF, SRC_PING
from noc.ip.models.prefix import Prefix
from noc.core.clickhouse.connect import connection
from noc.core.ip import IP, PrefixDB

ADDRESS_QUERY = """
    SELECT IPv4NumToString(ip) as address, pool, hostname, description
    FROM noc.purgatorium
    WHERE has(success_checks, 'ICMP') and date >= %s and source = 'network-scan'
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

        def get_vpn_id(ip):
            try:
                return vpn_db[IP.prefix(ip)]
            except KeyError:
                pass
            if self.object.vrf:
                return self.object.vrf.vpn_id
            return GLOBAL_VRF

        profile = self.get_artefact("profile_id")
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
            vpn_db[IP.prefix(p).first] = vpn_id
        address = []
        ts = datetime.datetime.now().replace(microsecond=0)
        ch = connection()
        r = ch.execute(ADDRESS_QUERY, args=[ts.date().isoformat()], return_raw=True)
        for row in r.splitlines():
            row = orjson.loads(row)
            address.append(
                DiscoveredAddress(
                    vpn_id=get_vpn_id(row["address"]),
                    address=row["address"],
                    profile=profile,
                    source=SRC_PING,
                    description=None,
                    subinterface=None,
                    mac=None,
                    fqdn=None,
                )
            )
        return address

    def is_enabled(self):
        return True
