# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DCN.DCWL.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx


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
        "n": "300000"
    }

    @classmethod
    def get_interface_speed(cls, name):
        c = cls.SPEED.get(name)
        return c

    def execute(self):
        result = []
        res = {}
        wres = {}
        w = self.cli("get radio all detail")
        for wline in w.splitlines():
            wr = wline.split(" ", 1)
            if wr[0] == "name":
                wname = wr[1].strip()
            elif wr[0] == "status":
                wstatus = wr[1].strip()
            elif wr[0].strip() == "mode":
                mode = wr[1].strip()
                speed = self.get_interface_speed(mode)
                wres[wname] = {"speed": speed, "status": wstatus}
        c = self.cli("get interface all detail")
        ssid = None
        for vline in c.splitlines():
            rr = vline.split(' ', 1)
            if rr[0] == "name":
                name = rr[1].strip()
            if rr[0] == "ssid":
                ssid = rr[1].strip().replace(" ", "").replace("Managed", "")
                if ssid.startswith("2a2d"):
                    # 2a2d - hex string
                    ssid = ssid.decode("hex")
            if rr[0] == "bss":
                bss = rr[1].strip()
            if ssid:
                res[name] = {"ssid": "%s.%s" % (name, ssid), "bss": bss}

        for s in res.values():
            v = self.cli("get bss %s detail" % s["bss"])
            for vline in v.splitlines():
                rr = vline.split(' ', 1)
                if rr[0] == "status":
                    status = rr[1].strip()
                if rr[0] == "radio":
                    radio = rr[1].strip()
                if rr[0] == "beacon-interface":
                    name = rr[1].strip()
                    if name in res.keys():
                        res[name].update({"radio": radio, "status": status})
        for o in res.items():
            status = o[1]["status"]
            if "up" in status:
                oper_status = True
            else:
                oper_status = False
            interface = o[1]["ssid"]
            for w in wres.items():
                if w[0] in o[1]["radio"]:
                    astatus = w[1]["status"]
                    if "up" in astatus:
                        admin_status = True
                    else:
                        admin_status = False
                    in_speed = w[1]["speed"]
                    out_speed = w[1]["speed"]
                    full_duplex = True
                    r = {
                        'interface': interface,
                        'admin_status': admin_status,
                        'oper_status': oper_status,
                        'full_duplex': full_duplex,
                        'in_speed': in_speed,
                        'out_speed': out_speed
                    }
                    result += [r]
        for o in res.items():
            status = o[1]["status"]
            if "up" in status:
                oper_status = True
            else:
                oper_status = False
            interface = o[0]
            for w in wres.items():
                if w[0] in o[1]["radio"]:
                    astatus = w[1]["status"]
                    if "up" in astatus:
                        admin_status = True
                    else:
                        admin_status = False
                    in_speed = w[1]["speed"]
                    out_speed = w[1]["speed"]
                    full_duplex = True
                    r = {
                        'interface': interface,
                        'admin_status': admin_status,
                        'oper_status': oper_status,
                        'full_duplex': full_duplex,
                        'in_speed': in_speed,
                        'out_speed': out_speed
                    }
                    result += [r]
        return result
