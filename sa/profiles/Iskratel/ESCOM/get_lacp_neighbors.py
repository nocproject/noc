# ---------------------------------------------------------------------
# Iskratel.ESCOM.get_lacp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlacpneighbors import IGetLACPNeighbors


class Script(BaseScript):
    name = "Iskratel.ESCOM.get_lacp_neighbors"
    interface = IGetLACPNeighbors

    rx_group_split = re.compile(r"\s+Group:\s+")
    rx_kv_search = re.compile(
        r"(?P<key>System ID|Partner|Group ID|"
        r"state|Max Ports|ports)\s:"
        r"\s(?P<value>.+?)(?:\s\s|$)",
        re.MULTILINE,
    )
    rx_port_split = re.compile(r"^Port:\s+", re.MULTILINE)
    rx_partner_info = re.compile(
        r"\s*Port\s+Flags\s+State\s+Pri\s+\|\s*Port\s+Pri\s+State\s+System"
        r"\s*(?P<actor_port>\S+)\s*([UFDA]+)\s*([aldpseg]+)\s*\d+\s*\|"
        r"\s*(?P<partner_port>\d+)\s*\d+\s*([aldpseg]+)\s*(?P<partner>\d+-\S+)"
    )

    def execute_cli(self):
        """

        # Exmple output:
                        Aggregator-group detail information(1)
                        --------------------------------------
        Group: 1
        ----------
        System ID : 32768 64EE.FFFF.0000    Partner : 32768 8426.BBBB.7777
         Group ID : 32768 64EE.FFFF.0028      state : lineUp
        Max Ports : 8                         ports : 1
        ------------------------------------------------------
        Flags: U - Port line status Up.            D - Port line status Down.
               F - lacp abled(FullDuplex Mode).    A - port Aggregated in Group.
        State: a - LACP is Running In Active Mode. p - LACP Passive Mode
               l - LACP Use LongTimeOut.           s - LACP synchronization.
               d - LACP use default setting.       e - LACP Expired.

        Port: tg1/1/8
          Status: Up     Aggregated
          Aggregator-group : 1    Mode : Lacp
          Lacp infomation
           Actor                      |Partner
           Port    Flags  State  Pri  |Port  Pri  State  System
           tg1/1/8 UFA    algs   0    |35906 32768ags    32768-32768 8426.BBBB.7777
            RX SM:    Current
            PT SM:    FastPeridic
            SL SM:    ready_N   ready
                      TRUE      TRUE      =>Selected
            Mx SM:    Aggregated
            Tx SM:    NTT       Count     Interval(ms)
                      FALSE     1         750

        :return:
        """
        r = []
        try:
            v = self.cli("show aggregator-group detail")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        port_id_map = {
            x["interface"]: x["ifindex"]
            for x in self.scripts.get_interface_properties(enable_ifindex=True)
        }
        for group in self.rx_group_split.split(v)[1:]:
            number, block = group.split("\n", 1)
            sections, *ports = self.rx_port_split.split(block)
            kv = dict(self.rx_kv_search.findall(sections))
            _, system_id = kv["System ID"].split(None, 1)
            bundle = []
            for port in ports:
                pi = self.rx_partner_info.search(port).groupdict()
                if not pi:
                    continue
                pi = dict(pi)
                _, partner_id = pi["partner"].split("-")
                actor_port = self.profile.convert_interface_name(pi["actor_port"])
                bundle += [
                    {
                        "interface": actor_port,
                        "local_port_id": port_id_map[actor_port],  # ifIndex
                        "remote_system_id": partner_id,
                        "remote_port_id": pi["partner_port"],
                    }
                ]
            r += [
                {
                    "lag_id": int(number),
                    "interface": f"Po {number}",
                    "system_id": system_id,
                    "bundle": bundle,
                }
            ]
        return r
