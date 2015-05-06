# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_inventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(NOCScript):
    name = "Brocade.IronWare.get_inventory"
    implements = [IGetInventory]

    rx_item_ch = re.compile(
        r"SL\s*(?P<slot>\d+):\s*(?P<part_no>\S+)\s+"
        r"(?P<descr>[ A-Za-z0-9,()\-]+)\n\s+"
        r"Serial\s*\S*\s*(?P<serial>\S+)",
        re.MULTILINE | re.DOTALL
    )
    rx_item_ti = re.compile(
        r"Serial\s*\S*\s*(?P<serial>\S+)", re.DOTALL
    )
    rx_item_rx = re.compile(
        r"SL\s*(M?\d*):\s*(\S+)\s*([ A-Za-z\-0-9]+)"
        r"\(Serial\s*\S+\s*([A-Za-z0-9]+),"
        r"\s*Part\s*\S+\s*([A-Za-z0-9\-]+)",
        re.DOTALL | re.MULTILINE
    )
    rx_chassis_rx = re.compile(
        r"^BigIron\s*(\S+)\s*CHASSIS\s*"
        r"\(Serial\s*\S+\s*([ A-Za-z0-9]+),"
        r"\s*Part\s*\S+\s*([ A-Za-z0-9\-]+)\)",
        re.DOTALL | re.IGNORECASE | re.MULTILINE
    )
    rx_chserial = re.compile(
        r"\s*Chassis\s*Serial\s*\S+\s*(?P<serial>\S+)", re.DOTALL)
    rx_hw = re.compile(r"HW:\s*(?P<platform>[ A-Za-z0-9]*)", re.DOTALL)
    rx_trans = re.compile("(1000Base\S+)")
    sx_power = re.compile(
        r"Power\s*supply\s*(\d)\s*\(([ A-Za-z\-]*)\)\s* present,"
        r"\s*status\s*ok\s*Model\s*Number:\s*(\S+)"
        r"\s*Serial\s*Number:\s*(\S+)\s*Firmware\s*Ver:\s*(\S+)",
        re.DOTALL | re.IGNORECASE | re.MULTILINE)
    rx_media_old = re.compile(r"(?P<port>\d/\d+):(?P<media>\S+)")
    rx_media_sx = re.compile(
        r"Port\s*(\d+/\d+):\s*Type\s*:\s*([A-Za-z\(\)0-9\- +]*)\s*?\n"
        r"(\s*\S+\s*)*?\n\s*Part\S\s*:\s*(\S+)\s*Serial\S\s*:\s*(\S+)",
        re.DOTALL | re.IGNORECASE)
    rx_media_rx = re.compile(
        r"Port\s*(\d*/\d*):\s*Type\s*:\s*([ A-Za-z0-9\-/\(\)]+)\s*"
        r"Vendor:\s*\S+\s*,\s*"
        r"Version:\s*\S+\s*"
        r"Part\S*\s*:\s*(\S+)\s*,\s*"
        r"Serial\S*\s*(\S+)",
        re.DOTALL | re.MULTILINE | re.IGNORECASE)

    TRANS_MAP = {
        "M-LX": "NoName | Transceiver | 1G | SFP LX",
        "C1550": "NoName | Transceiver | 1G | SFP LX",
        "C1510": "NoName | Transceiver | 1G | SFP LX",
        "1G M-LX(SFP)": "NoName | Transceiver | 1G | SFP LX",
        "1000BASEBX10D": "NoName | Transceiver | 1G | SFP BX (tx 1490nm)",
        "1000BASEBX10U": "NoName | Transceiver | 1G | SFP BX (tx 1310nm)",
        "M-TX": "NoName | Transceiver | 1G | SFP TX",
        "1G M-TX(SFP)": "NoName | Transceiver | 1G | SFP TX",
        "10G XG-ER(SFP+)": "NoName | Transceiver | 10G | SFP+ ER",
        "10GE LR 10km (SFP +)": "NoName | Transceiver | 10G | SFP+ LR",
        "UNKNOWN(SFP+)": "NoName | Transceiver | 10G | SFP+ LR",
        "10G-LR(xenpak)": "NoName | Transceiver | 10G | XenPak LR",
        "10G-ZR": "NoName | Transceiver | 10G | XenPak ZR"
    }

    def execute(self):
        objects = []
        v = self.cli("show version")
        media = self.cli("show media")
        match = self.rx_hw.search(v)
        if match:
            objects += [{
                "builtin": False,
                "description": "Chassis",
                "number": 0,
                "part_no": match.group("platform"),
                "serial": "None",
                "vendor": "BROCADE",
                "type": "CHASSIS"
            }]
        if "Turbo" in match.group("platform"):
            match1 = self.rx_item_ti.search(v)
            objects[0].update({"serial": match1.group("serial")})
            self.debug(media)
            for match2 in media.splitlines():
                nodata = ""
                if "Port" in match2:
                    partno = ""
                    l = match2.split()
                    self.debug(l)
                    if l[4] == "EMPTY":
                        port = ""
                    elif "M-TX" in match2:
                        nodata = "1"
                        port = l[1][:-1]
                        trans = " ".join(l[4:])
                        serial = "None"
                    elif "UNKNOWN" in match2:
                        nodata = "1"
                        port = l[1][:-1]
                        trans = " ".join(l[4:])
                        serial = "None"
                    else:
                        port = l[1][:-1]
                        self.debug(l[4])
                        self.debug(port)
                        trans = " ".join(l[4:])
                        serial = ""
                elif "Vendor" in match2:
                    l = match2.split()
                    self.debug(l)
                    descr = l[1]
                elif "Serial" in match2:
                    l = match2.split()
                    # descr=l[2]
                    if l[4]:
                        serial = l[4]
                    else:
                        serial = "SNUNKNOWN"
                    partno = l[2]
                # if match2[0].split("/")[0]==match1[0] and match2[1]!="EMPTY":
                # self.debug(match2)
                if nodata:
                    partno = self.TRANS_MAP[trans]
                if serial:
                    objects += [{
                        "builtin": False,
                        "description": trans,
                        "number": port,
                        "part_no": partno,
                        "serial": serial,
                        "type": "XCVR",
                        "vendor": "NONAME"
                    }]
        elif "SX" in match.group("platform"):
            chserial = self.rx_chserial.search(v)
            objects[0].update({"serial": chserial.group("serial")})
            power = self.cli("show chassis")
            for line in self.sx_power.findall(power):
                pwn = line[0]
                descr = line[1]
                partno = line[2]
                serial = line[3]
                objects += [{
                    "builtin": False,
                    "description": descr,
                    "number": pwn,
                    "part_no": partno,
                    "serial": serial,
                    "type": "PWR",
                    "vendor": "BROCADE"
                }]
            for match1 in self.rx_item_ch.findall(v):
                if "Mana" in match1[2]:
                    slot_type = "MGMT"
                else:
                    slot_type = "CARD"
                objects += [{
                    "builtin": False,
                    "description": match1[2],
                    "number": match1[0],
                    "part_no": match1[1],
                    "serial": match1[3],
                    "type": slot_type,
                    "vendor": "BROCADE"
                }]
                media = self.cli("show media slot %s" % match1[0])
                self.debug(media)
                for match2 in media.splitlines():
                    if "Port" in match2:
                        l = match2.split()
                        self.debug(l)
                        if l[4] == "EMPTY":
                            port = ""
                        else:
                            port = l[1][:-1].split("/")[1]
                            self.debug(l[4])
                            self.debug(port)
                            trans = " ".join(l[4:])
                            serial = ""
                    elif "Vendor" in match2:
                        l = match2.split()
                        self.debug(l)
                        descr = l[1]
                    elif "Serial" in match2:
                        l = match2.split()
                        self.debug(l)
                        #			descr=l[2]
                        if l[4]:
                            serial = l[4]
                        else:
                            serial = "SNUNKNOWN"
                        partno = l[2]
                        if not partno:
                            partno = self.TRANS_MAP[trans]
                        if serial:
                            objects += [{
                                "builtin": False,
                                "description": trans,
                                "number": port,
                                "part_no": partno,
                                "serial": serial,
                                "type": "XCVR",
                                "vendor": "NONAME"
                            }]
        elif "RX" in match.group("platform"):
            match = self.rx_chassis_rx.findall(v)[0]
            descr = match[0]
            serial = match[1]
            partno = match[2]
            objects[0].update({
                "serial": serial,
                "description": descr,
                "part_no": partno
            })
            # Power for RX-chassis
            power = self.cli("show chassis")
            for line in power.splitlines():
                if "Power" in line and not "Fail" in line:
                    if "Power" == line.split()[0]:
                        if "Installed" in line:
                            l = line.split()
                            pwn = l[1]
                            partno = l[2][1:]
                            descr = " ".join([l[4], l[5][:-2]])
                            serial = "None"
                            objects += [{
                                "builtin": False,
                                "description": descr,
                                "number": pwn,
                                "part_no": partno,
                                "serial": serial,
                                "type": "PWR",
                                "vendor": "BROCADE"
                            }]
            for l in v.splitlines():
                if "Fabric" in l:
                    partno = l.split(":")[2][:-1].strip()
                    descr = "RX-BI-SFM3 Switch Fabric Module"
                    n = l.split()[4]
                    serial = l.split(":")[1].split(",")[0].strip()
                    objects += [{
                        "builtin": False,
                        "description": descr,
                        "number": n,
                        "part_no": partno,
                        "serial": serial,
                        "type": "SFM",
                        "vendor": "BROCADE"
                    }]
            for match1 in self.rx_item_rx.findall(v):
                if "Mana" in match1[2]:
                    slot_type = "MGMT"
                    num = match1[0][1:]
                else:
                    slot_type = "CARD"
                    num = match1[0]
                objects += [{
                    "builtin": False,
                    "description": match1[1],
                    "number": num,
                    "part_no": match1[4],
                    "serial": match1[3],
                    "type": slot_type,
                    "vendor": "BROCADE"
                }]
                for trans in self.rx_media_rx.findall(media):
                    if trans[0].split("/")[
                        0] == num and slot_type == "CARD":
                        ntr = trans[0].split("/")[1]
                        descr = trans[1].strip()
                        partno = trans[2].strip()
                        serial = trans[3].strip()
                        if descr != "N/A":
                            objects += [{
                                "builtin": False,
                                "description": descr,
                                "number": ntr,
                                "part_no": partno,
                                "serial": serial,
                                "type": "XCVR",
                                "vendor": "NONAME"
                            }]
        else:
            # Old FastIron/BigIron chassis/objects
            serial = self.cli("show chassis").splitlines()[-1].split(":")[1].strip()
            objects[0].update({"serial": serial})
            for match1 in self.rx_item_ch.findall(v):
                objects += [{
                    "builtin": False,
                    "description": match1[2].split(",")[0],
                    "number": match1[0],
                    "part_no": match1[1],
                    "serial": match1[3],
                    "type": "MLC",
                    "vendor": "BROCADE"
                }]
                for match2 in self.rx_media_old.findall(media):
                    if match2[0].split("/")[0] == match1[0]:
                        objects += [{
                            "builtin": False,
                            "description": match2[1],
                            "number": match2[0].split("/")[1],
                            #				"number": match2[0],
                            "part_no": self.TRANS_MAP[match2[1]],
                            "serial": "SNUNKNOWN",
                            "type": "XCVR",
                            "vendor": "NONAME"
                        }]
        return objects
