# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_inventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
from itertools import groupby
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.sa.interfaces.base import InterfaceTypeError


class Script(BaseScript):
    name = "Cisco.IOS.get_inventory"
    interface = IGetInventory

    rx_item = re.compile(
        r"^NAME: \"(?P<name>[^\"]+)\", DESCR: \"(?P<descr>[^\"]+)\"\n"
        r"PID:\s+(?P<pid>\S+)?\s*,\s+VID:\s+(?P<vid>[\S ]+)?\s*, "
        r"SN: (?P<serial>\S+)", re.MULTILINE | re.DOTALL)
    rx_trans = re.compile("((?:100|1000|10G)BASE\S+)")
    rx_cvend = re.compile("(CISCO.(?P<ven>\S{3,15}))")
    rx_idprom = re.compile(
        r"\s*Vendor Name\s+(:|=)(\s+)?(?P<t_vendor>\S+[\S ]*)\n"
        r"(\s*Vendor OUI\s+(:|=)(\s+)?[\S+ ]*(\s+)?\n)?"
        r"\s*Vendor (PN|Part No.|Part Number)\s+(:|=)(\s+)?(?P<t_part_no>\S+[\S ]*)\n"
        r"\s*Vendor (rev|Revision|Part Rev.)\s+(:|=)(\s+)?(?P<t_rev>\S+[\S ]*)?\n"
        r"\s*Vendor (SN|Serial No.|Serial Number)\s+(:|=)(\s+)?(?P<t_sn>\S+)(\s+)?\n",
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

    rx_c4xk = re.compile(
        r"^Linecard\(slot\s(\d+)\)", re.IGNORECASE)

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
            if self.match_version(platform__regex=r"2[89]0[01]$"):
                # Inventory include motherboard for Cisco 2800 and 2900
                v = self.cli("show inventory raw")
            else:
                v = self.cli("show inventory")
            for match in self.rx_item.finditer(v):
                vendor, serial = "", ""
                if match.group("name") in self.IGNORED_NAMES:
                    continue
                type, number, part_no = self.get_type(
                    match.group("name"), match.group("pid"),
                    match.group("descr"), len(objects)
                )
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
                            print "!!! UNKNOWN: ", match.groupdict()
                            continue
                    elif type == 'MOTHERBOARD':
                        part_no = "CISCO%s-MB" % match.group("descr")[1:5]
                    else:
                        print "!!! UNKNOWN: ", match.groupdict()
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
                if (part_no in self.GBIC_MODULES or
                    "GBIC ETHERNET" in match.group("descr").upper()):
                        # Need get transceivers from idprom
                        objects += self.get_transceivers("sh int " +
                            "status module " + str(number))
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
                if (not s or "BaseTX" in s or s.startswith("Po")
                or "No Transceiver" in s):
                    continue
                else:
                    t_num = s.split()[0].split("/")[-1]
                    t_vendor, t_sn, t_rev, pid = self.get_idprom(s.split()[0], s.split()[-1].upper())
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
            print "%s command not supported" % cmd

    def get_idprom(self, int, descr):
        try:
            t = self.cli("show idprom int " + int + " | i Vendor")
            match = self.rx_idprom.search(t)
            if match:
                v = self.rx_cvend.search(match.group("t_vendor").upper())
                if v and "SYSTEMS" not in v.group("ven"):
                    t_vendor = v.group("ven")
                elif ("SYSTEMS" in match.group("t_vendor").upper()
                    and "CISCO" in match.group("t_vendor").upper()):
                        # Different variations of "CISCO@/-/_SYSTEMS" vendor
                        t_vendor = "CISCO"
                else:
                    # Others vendors
                    t_vendor = match.group("t_vendor").upper().strip()

                # Ignored serial
                t_sn = match.group("t_sn") if match.group("t_sn") not in self.IGNORED_SERIAL else None

                # Decode hex revision (need rewrite)
                if match.group("t_rev"):
                    t_rev = match.group("t_rev").strip()
                else:
                    t_rev = None
                if self.rx_trans.search(match.group("t_part_no").upper().replace("-", "")):
                    pid = self.get_transceiver_pid(match.group("t_part_no"))
                else:
                    if ("GBIC" in match.group("t_part_no") and
                       "Gi" in int):
                            pid = self.get_transceiver_pid("1000BASE" + match.group("t_part_no")[5:].strip())
                    else:
                        if "NONAME" in t_vendor and self.rx_trans.search(descr):
                            pid = self.get_transceiver_pid(descr)
                        else:
                            pid = match.group("t_part_no").strip()
                return t_vendor, t_sn, t_rev, pid
            else:
                return None, None, None, None
        except self.CLISyntaxError:
            print "sh idprom command not supported"
            return None, None, None, None


    def get_type(self, name, pid, descr, lo):
        """
        Get type, number and part_no
        """
        if pid is None:
            pid = ""
        if ("Transceiver" in descr or
                name.startswith("GigabitEthernet") or
                name.startswith("TenGigabitEthernet") or
                pid.startswith("X2-") or
                pid.startswith("XENPAK") or
                pid.startswith("Xenpak")):
            # Transceivers
            # Get number
            if name.startswith("Transceiver "):
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
            if pid in ("", "N/A", "Unspecified") or self.rx_trans.search(pid) \
            or len(list(groupby(pid))) == 1:
                # Non-Cisco transceivers
                pid = self.get_transceiver_pid(descr)
                if not pid:
                    return "XCVR", number, None
                else:
                    return "XCVR", number, pid
            else:
                # Normalization of pids "GBIC_LX/LH/BX"
                if (pid.startswith("GBIC_") and ("gigabit" in descr.lower()
                or "gigabit" in name.lower())):
                    pid = self.get_transceiver_pid("1000BASE" + pid[5:])
                return "XCVR", number, pid
        elif ("Motherboard" in name or "motherboard" in name
              or "Mother board" in name):
            # Motherboard for Cisco 2800, 2900
            if pid == "CISCO2801":
                return "MOTHERBOARD", None, "CISCO2801-MB"
            return "MOTHERBOARD", None, pid
        elif ((lo == 0 or pid.startswith("CISCO") or pid.startswith("WS-C"))
              and not pid.startswith("WS-CAC-") and not pid.endswith("-MB")
              and not "Clock" in descr and not "VTT FRU" in descr
              and not "C2801 Motherboard " in descr):
            try:
                number = int(name)
            except ValueError:
                number = None
            if pid in ("", "N/A"):
                if self.rx_7100.search(descr):
                    pid = "CISCO7100"
            return "CHASSIS", number, pid
        elif (("SUP" in pid or "S2U" in pid)
            and "supervisor" in descr):
                # Sup2
                try:
                    number = int(name)
                except ValueError:
                    number = None
                return "SUP", number, pid
        elif name.startswith("module "):
            # Linecards or supervisors
            if (pid.startswith("RSP")
            or ((pid.startswith("WS-SUP") or pid.startswith("VS-S"))
            and "Supervisor Engine" in descr)):
                return "SUP", name[7:], pid
            else:
                if (pid == "N/A" and "Gibraltar,G-20" in descr):
                    # 2-port 100BASE-TX Fast Ethernet port adapter
                    pid = "CISCO7100-MB"
                if pid == "ASR1001":
                    return "RP", name[7:], "ASR1001-RP"
                return "MOTHERBOARD", name[7:], pid
        elif ((pid.startswith("WS-X64") or pid.startswith("WS-X67")
              or pid.startswith("WS-X65")) and "port" in descr):
            try:
                number = int(name)
            except ValueError:
                number = None
            return "LINECARD", number, pid
        elif (((pid.startswith("WS-SUP") or pid.startswith("VS-S"))
        and "Supervisor Engine" in descr) or ((pid.startswith("C72")
        or pid.startswith("NPE") or pid.startswith("uBR7200-NPE")
        or pid.startswith("7301-NPE") or pid.startswith("7304-NPE"))
        and "Network Processing Engine" in descr)):
            try:
                number = int(name)
            except ValueError:
                number = None
            return "SUP", number, pid
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
            return "PSU", name.split()[1], pid
        elif name.startswith("Power Supply "):
            return "PSU", name.split()[2], pid
        elif "FRU Power Supply" in descr:
            return "PSU", name.split()[-1], pid
        elif " Power Supply" in name:
            if pid == "PWR-2911-AC":
                return "PSU", None, pid
            return "PSU", name[-1], pid
        elif pid.startswith("FAN"):
            # Fan module
            try:
                number = int(name[-1:])
            except:
                number = name.split()[1]
            return "FAN", number, pid
        elif (pid.startswith("NM-") or pid.startswith("NME-")
        or pid.startswith("EVM-") or pid.startswith("EM-")):
            # Network Module
            return "NM", name[-1], pid
        elif pid.startswith("SM-"):
            # ISR 2900/3900 ServiceModule
            return "SM", name[-1], pid
        elif "-NM-" in pid:
            # Network module 2
            if self.rx_c4xk.match(name):
                return "NM", self.rx_c4xk.match(name).group(1), pid
            return "NM", name.split()[5], pid
        elif (pid.startswith("WIC-") or pid.startswith("HWIC-")
              or pid.startswith("VWIC-") or pid.startswith("VWIC2-")
              or pid.startswith("EHWIC-") or pid.startswith("VWIC3-")
              or pid.startswith("VIC2-") or pid.startswith("VIC3-")):
                # DaughterCard
                return "DCS", name[-1], pid
        elif pid.startswith("AIM-"):
            # Network Module
            return "AIM", name[-1], pid
        elif (pid.startswith("PVDM2-") or pid.startswith("PVDM3-")):
            # PVDM Type 2 and 3
            return "PVDM", name[-1], pid
        elif pid.endswith("-MB"):
            # Motherboard
            return "MOTHERBOARD", None, pid
        elif pid.startswith("C3900-SPE"):
            # SPE for 3900
            return "SPE", name[-1], pid
        elif "Clock FRU" in descr:
            # Clock module
            return "CLK", name.split()[1], pid
        elif "VTT FRU" in descr:
            # Clock module
            return "VTT", name.split()[1], pid
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
