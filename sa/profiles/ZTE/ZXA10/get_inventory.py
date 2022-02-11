# ---------------------------------------------------------------------
# ZTE.ZXA10.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "ZTE.ZXA10.get_inventory"
    interface = IGetInventory

    type = {
        "PRSF": "PWR",
        "PRVR": "PWR",
        "PRWG": "PWR",
        "PRWGS": "PWR",
        "PRWH": "PWR",
        "PUMD": "PWR",
        "SCTM": "MAINBOARD",
        "SCXL": "MAINBOARD",
        "SCXM": "MAINBOARD",
        "SCXN": "MAINBOARD",
        "SFUQ": "MAINBOARD",
        "SMXA": "MAINBOARD",
        "SPUF": "MAINBOARD",
        "GMPA": "MAINBOARD",
        "GMRA": "MAINBOARD",
        "GFCL": "LINECARD",
        "GFGL": "LINECARD",
        "GUFQ": "LINECARD",
        "GUTQ": "LINECARD",
        "GUSQ": "LINECARD",
        "GTGHK": "LINECARD",
        "GTGHG": "LINECARD",
        "GTGOG": "LINECARD",
        "GTGOE": "LINECARD",
        "GTGQ": "LINECARD",
        "HUGQ": "LINECARD",
        "HUTQ": "LINECARD",
        "HUVQ": "LINECARD",
        "VDWVD": "LINECARD",
        "GVGO": "LINECARD",
        "PTWV": "LINECARD",
        "PTWVN": "LINECARD",
        "XFTO": "LINECARD",
        "ETGOD": "LINECARD",
        "ETGHG": "LINECARD",
        "ETGHK": "LINECARD",
        "FUMO": "FAN",
        "CVST": "unknown",
        "FCSDA": "unknown",
        "FCRDC": "unknown",
        "SVWMC": "unknown",
    }
    rx_platform = re.compile(r"^\d+\s+(?P<platform>\S+)MBRack\s+.+\n", re.MULTILINE)
    rx_card = re.compile(
        r"^Real-Type\s+:\s+(?P<type>\S+)\s+Serial-Number\s+:(?P<serial>.*)\n", re.MULTILINE
    )
    rx_card2 = re.compile(
        r"^CardName\s+:\s+(?P<type>\S+)\s*\n"
        r"^Status\s+:\s+\S+\s*\n"
        r"^Port-Number\s+:\s+\d+\s*\n"
        r"^Serial-Number\s+:(?P<serial>.*)\n",
        re.MULTILINE,
    )
    rx_detail = re.compile(r"Hardware-VER\s+:\s+(?P<hardware>\S+)\s*\n", re.MULTILINE)
    rx_tran = re.compile(
        r"^\s+Vendor-Name\s+:\s+(?P<vendor>.+)\s+Vendor-Pn\s+:\s+(?P<pn>.+)\n"
        r"^\s+Vendor-Sn\s+:\s+(?P<serial>.+)\s+Version-Lev\s+:\s+(?P<ver>.+)\n"
        r"^\s+Production-Date:\s+(?P<date>\S+)\s+",
        re.MULTILINE,
    )
    if_type = {
        "GUSQ": "gei_",
        "HUVQ": "gei_",
        "GMPA": "gei-",
        "GMRA": "gei-",
        "SFUQ": "xgei-",
        "SPUF": "xgei-",
        "XFTO": "xgei-",
        "GTGHK": "gpon-olt_",
        "GTGHG": "gpon-olt_",
        "GTGOG": "gpon-olt_",
        "GTGOE": "gpon-olt_",
        "GFCL": "gpon_olt-",
        "GFGL": "gpon_olt-",
        "GVGO": "gpon_olt-",
        "ETGHG": "epon-olt_",
        "ETGHK": "epon-olt_",
        "ETGOD": "epon-olt_",
        "VDWVD": "vdsl_",
        "SCXN": "gei_",
        "SCTM": "gei_",
        "SCXM": "gei_",
        "SCXL": "gei_",
        "SMXA": "gei_",
        "PTWVN": "",  # Telephone service
        "PRAM": "",
        "PRWGS": "",
    }

    def execute_cli(self):
        v = self.scripts.get_version()
        r = [{"type": "CHASSIS", "vendor": "ZTE", "part_no": [v["platform"]]}]
        if "attributes" in v:
            r[0]["serial"] = v["attributes"]["Serial Number"]
        ports = self.profile.fill_ports(self)
        for p in ports:
            v = self.cli("show card shelfno %s slotno %s" % (p["shelf"], p["slot"]))
            match = self.rx_card.search(v)
            if not match:
                match = self.rx_card2.search(v)
                if not match:
                    continue
            i = {
                "type": self.type[match.group("type")],
                "number": p["slot"],
                "vendor": "ZTE",
                "part_no": [match.group("type")],
            }
            if match.group("serial").strip():
                i["serial"] = match.group("serial").strip()
            match = self.rx_detail.search(v)
            if match and match.group("hardware") != "N/A":
                i["revision"] = match.group("hardware")
            r += [i]
            if int(p["port"]) < 1 or p["realtype"] == "":
                continue
            prefix = self.if_type[p["realtype"]]
            if prefix == "":
                continue
            for i in range(int(p["port"])):
                port_num = "%s/%s/%s" % (p["shelf"], p["slot"], str(i + 1))
                ifname = "%s%s" % (prefix, port_num)
                try:
                    v = self.cli("show interface optical-module-info %s" % ifname)
                except self.CLISyntaxError:
                    # In some card we has both gei_ and xgei_ interfaces
                    if prefix == "gei_":
                        ifname = "xgei_%s" % port_num
                        v = self.cli("show interface optical-module-info %s" % ifname)
                    if prefix == "gei-":
                        ifname = "xgei-%s" % port_num
                        v = self.cli("show interface optical-module-info %s" % ifname)
                match = self.rx_tran.search(v)
                if not match or "N/A" in match.group("vendor") or match.group("pn").strip() == "":
                    continue
                vendor = match.group("vendor").strip()
                part_no = match.group("pn").strip()
                if vendor == part_no:
                    vendor = "OEM"
                x = {
                    "type": "XCVR",
                    "vendor": vendor,
                    "serial": match.group("serial").strip(),
                    "part_no": part_no,
                    "number": str(i + 1),
                    "revision": match.group("ver").strip(),
                }
                date = match.group("date").strip()
                if date is not None and date.isdigit():
                    if len(date) == 8:
                        mfd = date[:4] + "-" + date[4:6] + "-" + date[6:]
                    else:
                        mfd = "20" + date[:2] + "-" + date[2:4] + "-" + date[4:]
                    x["mfg_date"] = mfd
                r += [x]
        return r
