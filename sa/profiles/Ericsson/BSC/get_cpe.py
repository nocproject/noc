# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Ericsson.BSC.get_cpe
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
    name = "Ericsson.BSC.get_cpe"
    interface = IGetCPE

    rx_cell = re.compile(r"(?P<cell>\d+)\s+ACTIVE",
                         re.MULTILINE)

    def execute(self):
        cpes = []
        with self.profile.mml(self):
            v = self.cli("RXMOP:MOTY=RXOTG;")
            for i in self.profile.iter_items(v):
                bsname = i["RSITE"]
                # bsid = i["TGFID"]
                bsmodel = i["MODEL"]
                swverrepl = i["SWVERREPL"]
                swverdld = i["SWVERDLD"]
                swveract = i["SWVERACT"]
                tmode = i["TMODE"]
                bsid = i["MO"]
                mo = i["MO"]
                SIPHASH_SEED = b"\x00" * 16
                bh = siphash24(SIPHASH_SEED, str(bsname))
                ip = "255.%d.%d.%d" % (ord(bh[0]), ord(bh[1]), ord(bh[2]))
                n = mo.split("-")
                scgr = n[1]
                sv = self.cli("RXMFP:MO=RXOCF-%s;" % scgr)
                platform = None
                sn = None
                for si in self.profile.iter_items(sv):
                    if "RU" in si and si["RU"] == "0":
                        platform = si["RUREVISION"]
                        sn = si["RUSERIALNO"]
                    else:
                        continue
                if not platform and not sn:
                    continue
                res = {
                    "vendor": "Ericsson",
                    "model": bsmodel,
                    "swverdld": swverdld,
                    "swveract": swveract,
                    "swverrepl": swverrepl,
                    "platform": platform,
                    "id": "%s:%s" % (bsid, sn),
                    "global_id": bsname,
                    "type": "bs",
                    "name": bsname,
                    "ip": ip,
                    "serial": sn,
                    "description": bsid,
                    "tmode": tmode
                }
                cpes += [res]
            c = self.cli("RLSTP:CELL=ALL;")
            for match in self.rx_cell.finditer(c):
                cellname = None
                cell = match.group("cell")
                cc = self.cli("RLDEP:CELL=%s;" % cell)
                cn = self.cli("RXTCP:MOTY=RXOTG,CELL=%s;" % cell)
                for st in self.profile.iter_items(cc):
                    if "CGI" in st:
                        cell_g_id = st["CGI"]
                    if "CSYSTYPE" in st:
                        csystype = st["CSYSTYPE"]
                    if "CELLIND" in st:
                        cellid = st["CELLIND"]
                SIPHASH_SEED = b"\x00" * 16
                bh = siphash24(SIPHASH_SEED, str(cell_g_id))
                ip = "255.%d.%d.%d" % (ord(bh[0]), ord(bh[1]), ord(bh[2]))
                for stn in self.profile.iter_items(cn):
                    if "MO" in stn:
                        cellname = stn["MO"] + "#" + stn["CELL"]
                    else:
                        continue
                if not cellname:
                    continue

                res = {
                    "vendor": "Ericsson",
                    "platform": "Sector",
                    "id": cellid,
                    "global_id": cell_g_id,
                    "type": "st",
                    "name": cellname,
                    "ip": ip,
                    "description": "",
                    "csystype": csystype
                }
                cpes += [res]
            return cpes
