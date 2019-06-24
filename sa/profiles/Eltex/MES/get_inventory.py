# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MES.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "Eltex.MES.get_inventory"
    interface = IGetInventory
    cache = True

    rx_hardware = re.compile(
        r"^HW version+\s+(?P<hardware>\S+)$", re.MULTILINE)
    rx_serial1 = re.compile(
        r"^Serial number :\s+(?P<serial>\S+)$", re.MULTILINE)
    rx_serial2 = re.compile(
        r"^\s+1\s+(?P<serial>\S+)\s*\n", re.MULTILINE)
    rx_serial3 = re.compile(
        r"^\s+1\s+(?P<mac>\S+)\s+(?P<hardware>\S+)\s+(?P<serial>\S+)\s*\n",
        re.MULTILINE)
    rx_platform = re.compile(
        r"^System Object ID:\s+(?P<platform>\S+)$", re.MULTILINE)
    rx_descr = re.compile(
        r"^System (?:Description|Type):\s+(?P<descr>.+)$", re.MULTILINE)
    rx_trans = re.compile(
        r"^\s*Transceiver information:\s*\n"
        r"^\s*Vendor name: (?P<vendor>.+?)\s*\n"
        r"^\s*Serial number: (?P<serial>.+?)\s*\n"
        r"(^\s*Part number: (?P<part_no>.+?)\s*\n)?"
        r"(^\s*Vendor revision: (?P<revision>.+?)\s*\n)?"
        r"^\s*Connector type: (?P<conn_type>.+?)\s*\n"
        r"^\s*Type: (?P<type>.+?)\s*\n"
        r"^\s*Compliance code: (?P<code>.+?)\s*\n"
        r"^\s*Laser wavelength: (?P<wavelength>.+?)\s*\n"
        r"^\s*Transfer distance: (?P<distance>.+?)\s*\n",
        re.MULTILINE
    )

    def get_chassis(self, plat, ver, ser):
        match = self.rx_descr.search(plat)
        if match and match.group("descr").startswith("MES"):
            descr = match.group("descr")
        else:
            descr = None

        platform = None
        match = self.rx_platform.search(plat)
        if match:
            platform = match.group("platform")
            platform = platform.split(".")[8]
            platform = self.profile.get_platform(platform)
        elif self.has_capability("Stack | Members"):
            # Try to obtain platform from description
            if descr and descr.startswith("MES"):
                platform = descr.split()[0]  # MES-3124F
                if not descr.startswith("MES-"):  # MES2208P
                    platform = "MES-%s" % platform[3:]

        hardware = self.rx_hardware.search(ver)

        match = self.rx_serial1.search(ser)
        match2 = self.rx_serial3.search(ser)
        if match:
            serial = self.rx_serial1.search(ser)
        elif match2:
            # Unit    MAC address    Hardware version Serial number
            # ---- ----------------- ---------------- -------------
            # 1   xx:xx:xx:xx:xx:xx     02.01.02      ESXXXXXXX
            serial = self.rx_serial3.search(ser)
        else:
            serial = self.rx_serial2.search(ser)

        r = {
            "type": "CHASSIS",
            "vendor": "ELTEX",
            "part_no": [platform]
        }
        if serial:
            r["serial"] = serial.group("serial")
        if hardware:
            r["revision"] = hardware.group("hardware")
        if descr:
            r["description"] = descr
        return r

    def get_trans(self, ifname):
        v = self.cli("show fiber-ports optical-transceiver detailed interface %s" % ifname)
        match = self.rx_trans.search(v)
        r = {
            "type": "XCVR",
            "vendor": match.group("vendor"),
        }
        if match.group("serial"):
            r["serial"] = match.group("serial")
        if match.group("revision"):
            r["revision"] = match.group("revision")
        if ifname.startswith("gi"):
            r["number"] = "gi%s" % ifname.split("/")[-1]
        if ifname.startswith("te"):
            r["number"] = "te%s" % ifname.split("/")[-1]
        if match.group("part_no"):
            part_no = match.group("part_no")
        else:
            r["vendor"] = "OEM"
            code = match.group("code")
            if code == "1000BASE-LX":
                part_no = "NoName | Transceiver | 1G | SFP LX"
            elif code == "BaseBX10":
                wavelength = match.group("wavelength")
                if wavelength == "1310 nm":
                    part_no = "NoName | Transceiver | 1G | SFP BX10D"
                elif wavelength == "1490 nm":
                    part_no = "NoName | Transceiver | 1G | SFP BX10U"
                else:
                    # raise self.NotSupportedError()
                    part_no = "NoName | Transceiver | 1G | SFP"
            elif code == "10GBASE-LR":
                part_no = "NoName | Transceiver | 10G | SFP+ LR"
            elif code == "unknown":
                part_no = "NoName | Transceiver | 1G | SFP"
            else:
                raise self.NotSupportedError()
        r["part_no"] = part_no
        return r

    def execute_cli(self, **kwargs):
        res = []
        ports = []

        try:
            v = self.cli("show fiber-ports optical-transceiver")
            for i in parse_table(v):
                if i[1] == "OK":
                    ports += [i[0]]
        except self.CLISyntaxError:
            pass

        if self.has_capability("Stack | Members"):
            for unit in self.capabilities["Stack | Member Ids"].split(" | "):
                plat = self.cli("show system unit %s" % unit, cached=True)
                if not self.is_has_image:
                    ver = self.cli("show version unit %s" % unit, cached=True)
                else:
                    ver = ""
                ser = self.cli("show system id unit %s" % unit, cached=True)
                r = self.get_chassis(plat, ver, ser)
                res += [r]
                for p in ports:
                    if p.startswith("gi") or p.startswith("te"):
                        if unit == p[2]:
                            res += [self.get_trans(p)]
        else:
            plat = self.cli("show system", cached=True)
            ver = self.cli("show version", cached=True)
            ser = self.cli("show system id", cached=True)
            r = self.get_chassis(plat, ver, ser)
            res = [r]
            for p in ports:
                res += [self.get_trans(p)]

        return res
