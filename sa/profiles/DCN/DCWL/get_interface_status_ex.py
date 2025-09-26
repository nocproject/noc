# ---------------------------------------------------------------------
# DCN.DCWL.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import codecs

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx
from noc.core.comp import smart_text


class Script(BaseScript):
    name = "DCN.DCWL.get_interface_status_ex"
    interface = IGetInterfaceStatusEx
    requires = []

    SPEED = {
        "bg-n": "300000",
        "a-n": "300000",
        "a-c": "1300000",
        "b-g": "54000",
        "bg": "54000",
        "a": "54000",
        "b": "11000",
        "g": "54000",
        "n": "300000",
    }

    @classmethod
    def get_interface_speed(cls, name):
        return cls.SPEED.get(name)

    def get_radio_status(self):
        r = {}
        w = self.cli("get radio all detail")

        for block in w.split("\n\n"):
            if not block:
                continue
            value = self.profile.table_parser(block)
            if "name" in value:
                r[value["name"]] = {
                    "status": value["status"] == "up",
                    "speed": self.get_interface_speed(value["mode"]),
                }
        return r

    def get_bss_status(self, bss):
        v = self.cli("get bss %s detail" % bss)
        value = self.profile.table_parser(v)
        if value.get("beacon-interface"):
            return {
                "oper_status": value["status"] == "up",
                "admin_status": value["global-radius"] == "on",
                "radio": value["radio"],
                "name": value["beacon-interface"],
            }

    def execute(self, interfaces=None):
        r = {}
        wres = self.get_radio_status()
        c = self.cli("get interface all detail")
        for block in c.split("\n\n"):
            value = self.profile.table_parser(block)
            if "name" not in value:
                self.logger.info("Ignoring unknown interface: '%s", value)
                continue
            ifname = value["name"]
            if value.get("bss") and value.get("ssid"):
                ssid = value["ssid"].replace(" ", "").replace("Managed", "")
                if ssid.startswith("2a2d"):
                    # 2a2d - hex string
                    ssid = smart_text(codecs.decode(ssid, "hex"))
                bss = self.get_bss_status(value["bss"])
                if not bss:
                    continue
                if_ssid = "%s.%s" % (ifname, ssid)
                r[ifname] = {
                    "interface": ifname,
                    "admin_status": bss["admin_status"],
                    "oper_status": bss["oper_status"],
                    "full_duplex": True,
                    "in_speed": wres[bss["radio"]]["speed"],
                    "out_speed": wres[bss["radio"]]["speed"],
                }
                r[if_ssid] = {
                    "interface": if_ssid,
                    "admin_status": bss["admin_status"],
                    "oper_status": bss["oper_status"],
                    "full_duplex": True,
                    "in_speed": wres[bss["radio"]]["speed"],
                    "out_speed": wres[bss["radio"]]["speed"],
                }
            elif ifname == "eth0":
                # Physical always up
                r[ifname] = {
                    "interface": ifname,
                    "admin_status": True,
                    "oper_status": True,
                    "full_duplex": True,
                    "in_speed": 100000,
                    "out_speed": 100000,
                }
        return list(r.values())
