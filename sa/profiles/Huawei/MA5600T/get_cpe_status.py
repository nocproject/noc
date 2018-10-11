# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.MA5600T.get_cpe_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re
import six
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcpe import IGetCPE
from noc.lib.text import parse_table_header
from noc.core.mib import mib


class Script(BaseScript):
    name = "Huawei.MA5600T.get_cpe_status"
    interface = IGetCPE

    cache = True

    splitter = re.compile("\s*-+\n")

    status_map = {
        "online": "active",  # associated
        "offline": "inactive",  # disassociating
    }

    def execute_cli(self, **kwargs):
        r = {}
        # v = self.cli("display ont info 0 all")
        for c in ["display ont info 0 all"]:
            v = self.cli(c)
            for table in v.split("\n\n"):
                tables_data = []
                parts = self.splitter.split(table)
                parts = parts[1:]
                while len(parts) > 2:
                    header, body = parts[:2]
                    parts = parts[2:]
                    head = parse_table_header(header.splitlines())
                    del head[2]  # remove empty header
                    tables_data += self.profile.parse_table1(body, head)
                else:
                    pass
                    # summary = parts
                for t in tables_data:
                    if "ONT-ID" in t:
                        ont_id = "%s/%s" % (t["F/S/P"][0].replace(" ", ""), t["ONT-ID"][0])
                        if ont_id in r:
                            r[ont_id]["description"] = t["Description"][0]
                        continue
                    status = "other"
                    if "ONT ID" in t:
                        ont_id, serial = t["ONT ID"][0].split()
                        status = self.status_map[t["Run state"][0]]
                    elif "ONT" in t:
                        #  -----------------------------------------------------------------------------
                        #  F/S/P   ONT         SN         Control     Run      Config   Match    Protect
                        #                       ID                     flag        state    state    state    side
                        #  -----------------------------------------------------------------------------
                        #
                        self.logger.warning("Shift header row. %s" % header)
                        ont_id, serial = t["ONT"][0].split()
                        status = self.status_map[t["Run ID"][0]]
                    # else:
                    #    self.logger.warning("Unknown ID")
                    #    continue
                    ont_id = "%s/%s" % (t["F/S/P"][0].replace(" ", ""), ont_id)
                    r[ont_id] = {
                        "interface": t["F/S/P"][0].replace(" ", ""),
                        "status": status,
                        "id": ont_id,
                        "global_id": serial + t["SN"][0],
                        "type": "ont",
                        "serial": serial + t["SN"][0],
                        "description": "",
                        "location": ""
                    }
        return list(six.itervalues(r))

    def execute_snmp(self, **kwargs):
        r = {}
        names = {x: y for y, x in six.iteritems(self.scripts.get_ifindexes(name_oid="IF-MIB::ifName"))}
        for ont_index, ont_serial, ont_descr in self.snmp.get_tables(
                [mib["HUAWEI-XPON-MIB::hwGponDeviceOntSn"],
                 mib["HUAWEI-XPON-MIB::hwGponDeviceOntDespt"]]
        ):
            ifindex, ont_id = ont_index.split(".")
            ont_id = "%s/%s" % (names[int(ifindex)], ont_id)
            r[ont_index] = {
                "interface": names[int(ifindex)],
                "status": "inactive",
                "id": ont_id,
                "global_id": ont_serial.encode("hex").upper(),
                "type": "ont",
                "serial": ont_serial.encode("hex").upper(),
                "description": ont_descr,
                "location": ""
            }
        for ont_index, ont_status in self.snmp.get_tables([mib["HUAWEI-XPON-MIB::hwGponDeviceOntControlRunStatus"]]):
            r[ont_index]["status"] = "active" if ont_status == 1 else "inactive"
        return six.itervalues(r)
