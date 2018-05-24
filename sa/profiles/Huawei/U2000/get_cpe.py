# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Huawei.U2000.get_cpe
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
from csiphash import siphash24
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcpe import IGetCPE


class Script(BaseScript):
    name = "Huawei.U2000.get_cpe"
    interface = IGetCPE

    rx_bs = re.compile(r"\s+BTS\sIndex\s+=\s+(?P<btsindex>\d+)\r\n"
                       r"\s+BTS\sName\s+=\s+(?P<btsname>\S.+)\r\n"
                       r"\s+BTS\sType\s+=\s+(?P<btstype>\S.*)\r\n"
                       r"\s+BTS\sDescription\s+=\s+(?P<btsdescr>\S.+)$",
                       re.MULTILINE)
    rx_cell = re.compile(r"\s+Cell\sIndex\s+=\s+(?P<cellindex>\d+)\r\n"
                         r"\s+Cell\sName\s+=\s+(?P<cellname>\d+)\r\n"
                         r"\s+Freq.\sBand\s+=\s+(?P<cellfreqband>\S+)\r\n"
                         r"[\S\s]+\r\n"
                         r"\s+BTS\sIndex\s+=\s+(?P<btsindex>\d+)\r\n"
                         r"\s+BTS\sName\s+=\s+(?P<btsname>\S.*)$",
                         re.MULTILINE)

    def execute(self):
        cpes = []
        cmd = self.mml("LST NEBYOMC")
        v = cmd.split("\r\n\r\n")[2]
        for line in v.splitlines():
            tp = line.split("   ")[0].strip()
            name = line.split("   ")[1].strip()
            ip = line.split("   ")[2].strip()
            if "BSC" in tp:
                with self.profile.mml_ne(self, ip):
                    bts = self.mml("LST BTS:LSTFORMAT=VERTICAL;")
                    for r in bts.split("\r\n\r\n"):
                        match = self.rx_bs.search(r)
                        if match:
                            btsindex = match.group("btsindex").strip()
                            btsname = match.group("btsname").strip()
                            btstype = match.group("btstype").strip()
                            btsdescr = match.group("btsdescr").strip()
                            SIPHASH_SEED = b"\x00" * 16
                            bh = siphash24(SIPHASH_SEED, str(btsname))
                            ip = "244.%d.%d.%d" % (ord(bh[0]), ord(bh[1]), ord(bh[2]))
                            res = {
                                "vendor": "Huawei",
                                "model": btstype,
                                "platform": name,
                                "id": "%s.%s" % (btsname, btsindex),
                                "global_id": "%s.%s" % (name, btsindex),
                                "type": "bs",
                                "name": btsname,
                                "ip": ip,
                                # "serial": sn,
                                "description": btsdescr
                                # "tmode": tmode
                            }
                            cpes += [res]

                    cell = self.mml("LST GCELL:LSTFORMAT=VERTICAL;")
                    for r in cell.split("\r\n\r\n"):
                        match = self.rx_cell.search(r)
                        if match:
                            cellindex = match.group("cellindex").strip()
                            cellname = match.group("cellname").strip()
                            btsindex = match.group("btsindex").strip()
                            btsname = match.group("btsname").strip()
                            SIPHASH_SEED = b"\x00" * 16
                            bh = siphash24(SIPHASH_SEED, str(cellname))
                            ip = "244.%d.%d.%d" % (ord(bh[0]), ord(bh[1]), ord(bh[2]))
                            res = {
                                "vendor": "Huawei",
                                "model": "Cell",
                                "platform": btsname,
                                "id": "%s.%s" % (cellname, cellindex),
                                "global_id": "%s.%s.%s" % (name, btsindex, cellindex),
                                "type": "st",
                                "name": "%s#%s" % (btsname, cellname),
                                "ip": ip,
                                # "serial": sn,
                                "description": btsname
                                # "tmode": tmode
                            }
                            cpes += [res]
            elif "BTS" in tp or "BNE" in tp:
                res = {
                    "vendor": "Huawei",
                    "model": tp,
                    "platform": "U2000",
                    "id": "LTE.%s" % name.split("_")[0],
                    "global_id": "".join(i for i in ip.split(".")),
                    "type": "bs",
                    "name": name,
                    "ip": ip,
                    # "serial": sn,
                    "description": name
                    # "tmode": tmode
                }
                cpes += [res]
            else:
                continue
        return cpes
