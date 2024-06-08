# ---------------------------------------------------------------------
# Huawei.MA5600T.get_cpe_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import codecs

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcpestatus import IGetCPEStatus
from noc.core.text import parse_table_header
from noc.core.mib import mib
from noc.core.snmp.render import render_bin
from noc.core.comp import smart_text


class Script(BaseScript):
    name = "Huawei.MA5600T.get_cpe_status"
    interface = IGetCPEStatus

    cache = True

    splitter = re.compile(r"\s*\n\s*-+\n")

    status_map = {"online": True, "offline": False}  # associated  # disassociating

    @staticmethod
    def fix_cpe_header(header):
        """
        Sometimes start line shift more than 15 spaces. Fix it
                                             F/S/P   ONT-ID   Description
        :param header:
        :return:
        """
        if len(header) > 0:
            # First line on header - 2
            header[0] = "  " + header[0].lstrip()
        if len(header) == 2:
            # Second line on header 10
            header[1] = " " * 10 + header[1].lstrip()
        return header

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
                    if not body:
                        # summary parts
                        continue
                    header = header.splitlines()
                    if any([h.startswith(" " * 15) for h in header]):
                        self.fix_cpe_header(header)
                    if not header:
                        continue
                    head = parse_table_header(header)
                    del head[2]  # remove empty header
                    tables_data += self.profile.parse_table1(body, head)
                for t in tables_data:
                    if "ONT-ID" in t:
                        ont_id = "%s/%s" % (t["F/S/P"][0].replace(" ", ""), t["ONT-ID"][0])
                        # if ont_id in r:
                        #    r[ont_id]["description"] = t["Description"][0]
                        continue
                    status = False
                    if "ONT ID" in t:
                        ont_id, serial = t["ONT ID"][0].split()
                        status = self.status_map[t["Run state"][0]]
                    elif "ONT" in t:
                        #  -----------------------------------------------------------------------------
                        #  F/S/P   ONT         SN         Control     Run      Config   Match    Protect
                        #                       ID                     flag        state    state    state    side
                        #  -----------------------------------------------------------------------------
                        #
                        self.logger.warning("Shift header row. %s" % "\n".join(header))
                        ont_id, serial = t["ONT"][0].split()
                        status = self.status_map[t["Run ID"][0]]
                    # else:
                    #    self.logger.warning("Unknown ID")
                    #    continue
                    ont_id = "%s/%s" % (t["F/S/P"][0].replace(" ", ""), ont_id)
                    r[ont_id] = {
                        "interface": t["F/S/P"][0].replace(" ", ""),
                        "oper_status": status,
                        "local_id": ont_id,
                        "global_id": serial + t["SN"][0],
                    }
        return list(r.values())

    def execute_snmp(self, **kwargs):
        r = {}
        names = {x: y for y, x in self.scripts.get_ifindexes(name_oid="IF-MIB::ifName").items()}
        for ont_index, ont_serial, ont_descr in self.snmp.get_tables(
            [
                mib["HUAWEI-XPON-MIB::hwGponDeviceOntSn"],
                mib["HUAWEI-XPON-MIB::hwGponDeviceOntDespt"],
            ],
            bulk=False,
            display_hints={mib["HUAWEI-XPON-MIB::hwGponDeviceOntSn"]: render_bin},
        ):
            ifindex, ont_id = ont_index.split(".")
            ont_id = "%s/%s" % (names[int(ifindex)], ont_id)
            r[ont_index] = {
                "interface": names[int(ifindex)],
                "oper_status": False,
                "local_id": ont_id,
                "global_id": smart_text(codecs.encode(ont_serial, "hex")).upper(),
            }
        for ont_index, ont_status in self.snmp.get_tables(
            [mib["HUAWEI-XPON-MIB::hwGponDeviceOntControlRunStatus"]]
        ):
            r[ont_index]["status"] = "active" if ont_status == 1 else "inactive"
        return list(r.values())
