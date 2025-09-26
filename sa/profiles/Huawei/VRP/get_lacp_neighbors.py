# ---------------------------------------------------------------------
# Huawei.VRP.get_lacp_neighbors
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
    name = "Huawei.VRP.get_lacp_neighbors"
    interface = IGetLACPNeighbors

    split_re = re.compile(r"(\S+')s state information is:", re.IGNORECASE)
    re_kv_searh = re.compile(
        r"(?P<key>LAG ID|WorkingMode|System ID|"
        r"Operate status|System Priority|Hash arithmetic):"
        r"\s(?P<value>.+?)(?:\s\s|$)",
        re.MULTILINE,
    )
    rx_split_section = re.compile(r"(?:Local\:|Partner\:)")
    rx_table_header = re.compile(r"--------------+")

    def execute_cli(self):
        """

        # Exmple output:
        Block1:
        Local:
        LAG ID: 8                   WorkingMode: LACP
        Preempt Delay: Disabled     Hash arithmetic: According to SIP-XOR-DIP
        System Priority: 32768      System ID: 5119-9225-3425
        Least Active-linknumber: 1  Max Active-linknumber: 8
        Operate status: up          Number Of Up Port In Trunk: 2
        --------------------------------------------------------------------------------
        ActorPortName          Status   PortType PortPri PortNo PortKey PortState Weight
        XGigabitEthernet10/0/4 Selected 10GE     32768   95     2113    10111100  1
        XGigabitEthernet10/0/5 Selected 10GE     32768   96     2113    10111100  1

        Block2:
        Partner:
        --------------------------------------------------------------------------------
        ActorPortName          SysPri   SystemID        PortPri PortNo PortKey PortState
        XGigabitEthernet10/0/4 65535    0011-bbbb-ddda  255     1      33      10111100
        XGigabitEthernet10/0/5 65535    0011-bbbb-ddda  255     2      33      10111100

        :return:
        """
        r = []
        try:
            v = self.cli("display eth-trunk")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        if "No valid trunk in the system" in v:
            return r
        pc_name = None
        for block in self.split_re.split(v):
            # print("Split %s" % self.split_re.split(v))
            if not block:
                continue
            if block.endswith("'"):
                pc_name = block.strip("'")
                continue
            if not pc_name:
                self.logger.debug("Unknown interface")
                continue
            self.logger.debug("[%s] Block is: %s", pc_name, block)
            section = self.rx_split_section.split(block.strip())
            if "" in section:
                section.remove("")
            if len(section) == 1:
                self.logger.error("[%s] Not partner. Skipping", pc_name)
                continue
            if len(section) == 2:
                local, partner = section
            else:
                self.logger.error("[%s] Multiple section on out. Skipping", pc_name)
                continue
            local_dict, local = self.rx_table_header.split(local)
            local_dict = dict(self.re_kv_searh.findall(local_dict))
            local = local.strip().splitlines()
            # loca_port_map = {local[]}
            bundle = []
            _, partner = self.rx_table_header.split(partner)
            partner = partner.strip().splitlines()
            partner_map = {
                x["ActorPortName"]: {"SystemID": x["SystemID"], "PortNo": x["PortNo"]}
                for x in [dict(zip(partner[0].split(), p.split())) for p in partner[1:]]
            }
            for bun in local[1:]:
                bun = dict(zip(local[0].split(), bun.split()))
                # print("Bundle %s" % bun)
                if not bun:
                    continue
                if not partner_map or bun["ActorPortName"] not in partner_map:
                    continue
                bundle += [
                    {
                        "interface": bun["ActorPortName"],
                        "local_port_id": int(bun["PortNo"]),
                        "remote_system_id": partner_map[bun["ActorPortName"]]["SystemID"],
                        "remote_port_id": partner_map[bun["ActorPortName"]]["PortNo"],
                    }
                ]
            r += [
                {
                    "lag_id": int(local_dict["LAG ID"]),
                    "interface": pc_name,
                    "system_id": local_dict["System ID"],
                    "bundle": bundle,
                }
            ]
        return r
