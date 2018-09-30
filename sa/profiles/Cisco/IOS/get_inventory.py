# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.IOS.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from itertools import groupby
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.lib.validators import is_int


class Script(BaseScript):
    name = "Cisco.IOS.get_inventory"
    interface = IGetInventory

    rx_item = re.compile(
        r"^NAME: \"(?P<name>[^\"]+)\", DESCR: \"(?P<descr>[^\"]+)\"\n"
        r"PID:\s+(?P<pid>\S+)?\s*,\s+VID:\s+(?P<vid>\S+)?\s*, "
        r"SN:\s(?P<serial>\S+)?", re.MULTILINE | re.DOTALL)
    rx_trans = re.compile("((?:100|1000|10G)BASE\S+)")
    rx_cvend = re.compile("(CISCO.(?P<ven>\S{3,15}))")
    rx_idprom = re.compile(
        r"\s*Vendor Name\s+(:|=)(\s+)?(?P<t_vendor>\S+[\S ]*)\n"
        r"(\s*Vendor OUI\s+(:|=)(\s+)?[\S+ ]*(\s+)?\n)?"
        r"\s*Vendor (PN|Part No.|Part Number)\s+(:|=)(\s+)?(?P<t_part_no>\S+"
        r"[\S ]*)\n"
        r"\s*Vendor (rev|Revision|Part Rev.)\s+(:|=)(\s+)?(?P<t_rev>\S+"
        r"[\S ]*)?\n"
        r"\s*Vendor (SN|Serial No.|Serial Number)\s+(:|=)(\s+)?(?P<t_sn>\S+)"
        r"(\s+)?\n",
        re.IGNORECASE | re.MULTILINE | re.DOTALL)
    rx_ver = re.compile(
        r"Model revision number\s+:\s+(?P<revision>\S+)\s*\n"
        r"Motherboard revision number\s+:\s+\S+\s*\n"
        r"Model number\s+:\s+(?P<part_no>\S+)\s*\n"
        r"System serial number\s+:\s+(?P<serial>\S+)\s*\n",
        re.IGNORECASE | re.MULTILINE | re.DOTALL)
    rx_ver1 = re.compile(
        r"^cisco (?P<part_no>\S+) \(\S+\) processor( "
        r"\(revision(?P<revision>.+?)\))? with",
        re.IGNORECASE | re.MULTILINE)
    rx_7100 = re.compile(
        r"^(?:uBR|CISCO)?71(?:20|40|11|14)(-\S+)? "
        r"(?:Universal Broadband Router|chassis)")
    rx_slot_id = re.compile(
        r"^.*(slot|[tr|b]ay|pem|supply|fan|module)(\s*:?)"
        r"(?P<slot_id>[\d|\w]+).*", re.IGNORECASE)
    rx_psu1 = re.compile("(?:PS|Power Supply) (?P<number>\d+) ")
    rx_psu2 = re.compile("Power Supply (?P<number>\d+)$")

    slot_id = 0

    IGNORED_SERIAL = set([
        "H22L714"
    ])

    IGNORED_NAMES = set([
        "c7201"
    ])

    GBIC_MODULES = set([
        "WS-X6K-SUP2-2GE",
        "WS-X6724-SFP"
    ])

    ISR_MB = set([
        "CISCO2801",
        "CISCO2811"
    ])

    def get_inv(self):
        objects = []
        try:
            v = self.cli("show inventory raw")
            self.slot_id = 0
            for match in self.rx_item.finditer(v):
                vendor, serial = "", ""
                if match.group("name") in self.IGNORED_NAMES:
                    self.logger.debug(
                        "Part %s in ignored name. Skipping" % match.group("name")
                    )
                    continue
                self.logger.debug(
                    "Get type: %s, %s, %s", match.group("name"),
                    match.group("pid"), match.group("descr")
                )
                type, number, part_no = self.get_type(
                    match.group("name"), match.group("pid"),
                    match.group("descr"), len(objects)
                )
                self.logger.debug("Return: %s, %s, %s", type, number, part_no)
                if type == "SLOTID":
                    self.logger.debug("Type equal slot_id")
                    self.slot_id = number
                    continue
                if (
                    not match.group("pid") and not match.group("vid") and
                    not match.group("serial")
                ):
                    self.logger.debug("PID, VID, Serial is not match. Continue...")
                    continue
                serial = match.group("serial")
                if not part_no:
                    if type and "XCVR" in type:
                        # Last chance to get idprom
                        if match.group("name").startswith("Transceiver"):
                            int = match.group("name").split()[1]
                        elif match.group("name").startswith("GigabitEthernet"):
                            int = match.group("name").split()[0]
                        else:
                            int = match.group("name")
                        vendor, t_sn, t_rev, part_no = self.get_idprom(
                            int, match.group("descr").upper()
                        )
                        if not serial:
                            serial = t_sn
                        if not part_no:
                            continue
                    elif type == 'MOTHERBOARD':
                        part_no = "CISCO%s-MB" % match.group("descr")[1:5]
                    else:
                        continue
                if serial in self.IGNORED_SERIAL:
                    serial = None
                if part_no in self.ISR_MB and type == 'MOTHERBOARD':
                    part_no = "%s-MB" % part_no
                if not vendor:
                    if "NoName" in part_no or "Unknown" in part_no:
                        vendor = "NONAME"
                    else:
                        vendor = "CISCO"
                objects += [{
                    "type": type,
                    "number": number,
                    "vendor": vendor,
                    "serial": serial,
                    "description": match.group("descr"),
                    "part_no": [part_no],
                    "revision": match.group("vid"),
                    "builtin": False
                }]

                # if gbic slots in module
                if (
                    part_no in self.GBIC_MODULES or
                    "GBIC ETHERNET" in match.group("descr").upper()
                ):
                    # Need get transceivers from idprom
                    objects += self.get_transceivers(
                        "sh int " + "status module " + str(number)
                    )
        except self.CLISyntaxError:
            c = self.cli("show version", cached=True)
            match = self.rx_ver.search(c)
            if match:
                return [{
                    "type": "CHASSIS",
                    "vendor": "CISCO",
                    "serial": match.group("serial"),
                    "part_no": [match.group("part_no")],
                    "revision": match.group("revision"),
                    "builtin": False
                }]
            else:
                match = self.rx_ver1.search(c)
                if match:
                    return [{
                        "type": "CHASSIS",
                        "vendor": "CISCO",
                        "part_no": [match.group("part_no")],
                        "revision": match.group("revision"),
                        "builtin": False
                    }]
                else:
                    raise self.NotSupportedError()
        return objects

    def get_transceivers(self, cmd):
        try:
            # Get phy interfaces
            i = self.cli(cmd)
            objects = []
            for s in i.split("\n"):
                if (
                    not s or "BaseTX" in s or s.startswith("Po") or
                    "No Transceiver" in s
                ):
                    continue
                else:
                    t_num = s.split()[0].split("/")[-1]
                    t_vendor, t_sn, t_rev, pid = \
                        self.get_idprom(s.split()[0], s.split()[-1].upper())
                    if not pid:
                        self.logger.debug("PID on Transiever: :%s is not set. Skipping...", s)
                        continue
                    objects += [{
                        "type": "XCVR",
                        "number": t_num,
                        "vendor": t_vendor,
                        "serial": t_sn,
                        "description": s.split()[-1] + " Transceiver",
                        "part_no": [pid],
                        "revision": t_rev,
                        "builtin": False
                    }]
            return objects
        except self.CLISyntaxError:
            pass

    def get_idprom(self, int, descr):
        try:
            t = self.cli("show idprom int %s | i Vendor" % int)
            match = self.rx_idprom.search(t)
            if match:
                v = self.rx_cvend.search(match.group("t_vendor").upper())
                if v and "SYSTEMS" not in v.group("ven"):
                    t_vendor = v.group("ven")
                elif (
                    "SYSTEMS" in match.group("t_vendor").upper() and
                    "CISCO" in match.group("t_vendor").upper()
                ):
                        # Different variations of "CISCO@/-/_SYSTEMS" vendor
                        t_vendor = "CISCO"
                else:
                    # Others vendors
                    t_vendor = match.group("t_vendor").upper().strip()

                # Ignored serial
                t_sn = match.group("t_sn") \
                    if match.group("t_sn") not in self.IGNORED_SERIAL else None

                # Decode hex revision (need rewrite)
                if match.group("t_rev"):
                    t_rev = match.group("t_rev").strip()
                else:
                    t_rev = None
                if self.rx_trans.search(
                    match.group("t_part_no").upper().replace("-", "")
                ):
                    pid = self.get_transceiver_pid(match.group("t_part_no"))
                else:
                    if "GBIC" in match.group("t_part_no") and "Gi" in int:
                        pid = self.get_transceiver_pid(
                            "1000BASE" +
                            match.group("t_part_no")[5:].strip()
                        )
                    else:
                        if (
                            "NONAME" in t_vendor and
                            self.rx_trans.search(descr)
                        ):
                            pid = self.get_transceiver_pid(descr)
                        else:
                            pid = match.group("t_part_no").strip()
                return t_vendor, t_sn, t_rev, pid
            else:
                return None, None, None, None
        except self.CLISyntaxError:
            return None, None, None, None

    def get_type(self, name, pid, descr, lo):
        """
        Get type, number and part_no
        """
        if pid is None:
            if (
                "Motherboard" in name or "motherboard" in name or
                "Mother board" in name
            ):
                # Cisco ISR series not have PID for motherboard
                if "1921" in name:
                    return "MOTHERBOARD", None, "CISCO1921-MB"
                elif "2901" in name:
                    return "MOTHERBOARD", None, "CISCO2901-MB"
                elif "2911" in name:
                    return "MOTHERBOARD", None, "CISCO2911-MB"
                elif "2921" in name:
                    return "MOTHERBOARD", None, "CISCO2921-MB"
            pid = ""
            match = self.rx_slot_id.search(name)
            if match:
                if (
                    "Container of Fan FRU" in name or
                    "Container of Power Supply" in name or
                    "Power Supply Container" in name or
                    "Module Temperature Sensor" in name or
                    "Supply Voltage Sensor" in name
                ):
                    return "SLOTID", None, None
                return "SLOTID", match.group("slot_id"), None
        if (
            "Transceiver" in descr or
            name.startswith("GigabitEthernet") or
            name.startswith("TenGigabitEthernet") or
            pid.startswith("X2-") or
            pid.startswith("XENPAK") or
            pid.startswith("Xenpak") or
            name.startswith("Converter")
        ):
            # Transceivers
            # Get number
            if (
                name.startswith("Transceiver ") or
                name.startswith("Converter ")
            ):
                # Get port number
                _, number = name.rsplit("/", 1)
            elif name.startswith("GigabitEthernet"):
                number = name.split(" ", 1)[0].split("/")[-1]
            elif name.startswith("Te"):
                if " " in name:
                    number = name.split(" ", 1)[0].split("/")[-1]
                else:
                    number = name.split("/")[-1]
            else:
                number = None
            if (
                pid in ("", "N/A", "Unspecified") or
                self.rx_trans.search(pid) or len(list(groupby(pid))) == 1
            ):
                # Non-Cisco transceivers
                pid = self.get_transceiver_pid(descr)
                if not pid:
                    return "XCVR", number, None
                else:
                    return "XCVR", number, pid
            else:
                # Normalization of pids "GBIC_LX/LH/BX"
                if (
                    pid.startswith("GBIC_") and (
                        "gigabit" in descr.lower() or
                        "gigabit" in name.lower()
                    )
                ):
                    pid = self.get_transceiver_pid("1000BASE" + pid[5:])
                return "XCVR", number, pid
        elif (
            "Motherboard" in name or "motherboard" in name or
            "Mother board" in name
        ):
            # Motherboard for Cisco 2800, 2900
            if pid == "CISCO2801":
                return "MOTHERBOARD", None, "CISCO2801-MB"
            elif "1921" in name:
                return "MOTHERBOARD", None, "CISCO1921-MB"
            return "MOTHERBOARD", None, pid
        elif (
            pid.startswith("WS-X4920") or
            (pid.startswith("WS-C4900M") and "Linecard" in name)
        ):
            return "LINECARD", self.slot_id, pid
        elif (
            (lo == 0 or pid.startswith("CISCO") or pid.startswith("WS-C")) and
            not pid.startswith("WS-CAC-") and not pid.endswith("-MB") and
            "Clock" not in descr and "VTT FRU" not in descr and
            "C2801 Motherboard " not in descr
        ):
            if pid in ("", "N/A"):
                if self.rx_7100.search(descr):
                    pid = "CISCO7100"
            if (len(pid) - len(descr) == 2) and pid[len(descr)] == "-":
                pid = descr
            if is_int(name):  # Stacking
                return "CHASSIS", int(name), pid
            return "CHASSIS", self.slot_id, pid
        elif ("SUP" in pid or "S2U" in pid) and "supervisor" in descr:
            # Sup2
            return "SUP", self.slot_id, pid
        elif name.startswith("module "):
            # Linecards or supervisors
            if (
                pid.startswith("RSP") or (
                    (
                        pid.startswith("WS-SUP") or pid.startswith("VS-S")
                    ) and "Supervisor Engine" in descr
                )
            ):
                return "SUP", self.slot_id, pid
            else:
                if pid == "N/A" and "Gibraltar,G-20" in descr:
                    # 2-port 100BASE-TX Fast Ethernet port adapter
                    pid = "CISCO7100-MB"
                if pid in ("ASR1001", "ASR1001-X"):
                    return "RP", self.slot_id, pid + "-RP"
                return "MOTHERBOARD", self.slot_id, pid
        elif (
            (
                pid.startswith("WS-X64") or pid.startswith("WS-X67") or
                pid.startswith("WS-X65") or pid.startswith("WS-X68")
            ) and "port" in descr
        ):
            return "LINECARD", self.slot_id, pid
        elif (
            (
                (pid.startswith("WS-SUP") or pid.startswith("VS-S")) and
                "Supervisor Engine" in descr
            ) or (
                (
                    pid.startswith("C72") or
                    pid.startswith("NPE") or pid.startswith("uBR7200-NPE") or
                    pid.startswith("7301-NPE") or pid.startswith("7304-NPE")
                ) and "Network Processing Engine" in descr
            )
        ):
            return "SUP", self.slot_id, pid
        elif "-PFC" in pid:
            # PFC subcard
            return "PFC", None, pid
        elif name.startswith("msfc "):
            # MSFC subcard
            return "MSFC", None, pid
        elif "-DFC" in pid or "-CFC" in pid or "sub-module of" in name:
            # DFC subcard
            return "DFC", None, pid
        elif name.startswith("PS "):
            # Power supply
            match = self.rx_psu1.search(name)
            if match:
                self.slot_id = int(match.group("number"))
            return "PSU", self.slot_id, pid
        elif name.startswith("Power Supply "):
            match = self.rx_psu1.search(name)
            if match:
                self.slot_id = int(match.group("number"))
            return "PSU", self.slot_id, pid
        elif "FRU Power Supply" in descr:
            match = self.rx_psu2.search(name)
            if match:
                self.slot_id = int(match.group("number"))
            return "PSU", self.slot_id, pid
        elif " Power Supply" in name:
            if pid == "PWR-2911-AC":
                return "PSU", None, pid
            match = self.rx_psu2.search(name)
            if match:
                self.slot_id = int(match.group("number"))
            return "PSU", self.slot_id, pid
        elif pid.startswith("FAN") or pid == "WS-X4992":
            # Fan module
            return "FAN", self.slot_id, pid
        elif (
            pid.startswith("NM-") or pid.startswith("NME-") or
            pid.startswith("EVM-") or pid.startswith("EM-")
        ):
            # Network Module
            return "NM", self.slot_id, pid
        elif pid.startswith("SM-"):
            # ISR 2900/3900 ServiceModule
            return "SM", self.slot_id, pid
        elif "-NM-" in pid:
            # Network module 2
            return "NM", self.slot_id, pid
        elif (
            pid.startswith("WIC-") or pid.startswith("HWIC-") or
            pid.startswith("VWIC-") or pid.startswith("VWIC2-") or
            pid.startswith("EHWIC-") or pid.startswith("VWIC3-") or
            pid.startswith("VIC2-") or pid.startswith("VIC3-")
        ):
            # DaughterCard
            return "DCS", self.slot_id, pid
        elif pid.startswith("AIM-"):
            # Network Module
            return "AIM", self.slot_id, pid
        elif pid.startswith("PVDM2-") or pid.startswith("PVDM3-"):
            # PVDM Type 2 and 3
            return "PVDM", self.slot_id, pid
        elif pid.endswith("-MB"):
            # Motherboard
            return "MOTHERBOARD", None, pid
        elif pid.startswith("C3900-SPE"):
            # SPE for 3900
            return "SPE", self.slot_id, pid
        elif "Clock FRU" in descr:
            # Clock module
            return "CLK", self.slot_id, pid
        elif "VTT FRU" in descr:
            # Clock module
            return "VTT", self.slot_id, pid
        elif "Compact Flash Disk" in descr:
            # Compact Flash
            return "Flash | CF", name, pid
        # Unknown
        return None, None, None

    def get_transceiver_pid(self, descr):
        match = self.rx_trans.search(descr.upper().replace("-", ""))
        if match:
            return "Unknown | Transceiver | %s" % match.group(1).upper()
        return None

    @BaseScript.match(platform__regex=r"C2960")
    def execute_2960(self):
        objects = self.get_inv()
        objects += self.get_transceivers("show int status")
        return objects

    @BaseScript.match()
    def execute_others(self):
        objects = self.get_inv()
        return objects
