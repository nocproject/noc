# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_inventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
from itertools import groupby
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.sa.interfaces.base import InterfaceTypeError


class Script(NOCScript):
    name = "Cisco.IOS.get_inventory"
    implements = [IGetInventory]

    rx_item = re.compile(
        r"^NAME: \"(?P<name>[^\"]+)\", DESCR: \"(?P<descr>[^\"]+)\"\n"
        r"PID:\s+(?P<pid>\S+)?\s*,\s+VID:\s+(?P<vid>[\S ]+)?\s*, SN: (?P<serial>\S+)",
        re.MULTILINE | re.DOTALL
    )
    rx_trans = re.compile("((?:100|1000|10G)BASE\S+)")
    rx_cvend = re.compile("(CISCO.(?P<ven>\S{3,15}))")
    rx_idprom = re.compile(
        r"\s*Vendor Name\s+(:|=)(\s+)?(?P<t_vendor>\S+[\S ]*)\n"
        r"(\s*Vendor OUI\s+(:|=)(\s+)?[\S+ ]*(\s+)?\n)?"
        r"\s*Vendor (PN|Part No.|Part Number)\s+(:|=)(\s+)?(?P<t_part_no>\S+[\S ]*)\n"
        r"\s*Vendor (rev|Revision|Part Rev.)\s+(:|=)(\s+)?(?P<t_rev>\S+[\S ]*)?\n"
        r"\s*Vendor (SN|Serial No.|Serial Number)\s+(:|=)(\s+)?(?P<t_sn>\S+)(\s+)?\n",
        re.IGNORECASE | re.MULTILINE | re.DOTALL
    )
    rx_ver = re.compile(
        r"Model revision number\s+:\s+(?P<revision>\S+)\s*\n"
        r"Motherboard revision number\s+:\s+\S+\s*\n"
        r"Model number\s+:\s+(?P<part_no>\S+)\s*\n"
        r"System serial number\s+:\s+(?P<serial>\S+)\s*\n",
        re.IGNORECASE | re.MULTILINE | re.DOTALL
    )

    IGNORED_SERIAL = set([
        "H22L714"
    ])

    IGNORED_NAMES = set([
        "c7201"
    ])

    GBIC_MODULES = set([
        "WS-X6K-SUP2-2GE"
    ])

    def get_inv(self):
        objects = []
        try:
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
                    else:
                        print "!!! UNKNOWN: ", match.groupdict()
                        continue
                if serial in self.IGNORED_SERIAL:
                    serial = None
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
            v = self.rx_ver.search(self.cli("show version"))
            if v:
                return [{
                    "type": "CHASSIS",
                    "vendor": "CISCO",
                    "serial": match.group("serial"),
                    "part_no": [match.group("part_no")],
                    "revision": match.group("revision"),
                    "builtin": False
                }]
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
                elif "OEM" in match.group("t_vendor").upper():
                    # China noname products with "OEM" vendor
                    t_vendor = "NONAME"
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
                pid.startswith("XENPAK")):
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
        elif ((lo == 0 or pid.startswith("CISCO") or pid.startswith("WS-C"))
        and not pid.startswith("WS-CAC-") and not pid.endswith("-MB")
        and not "Clock" in descr and not "VTT FRU" in descr):
            try:
                number = int(name)
            except ValueError:
                number = None
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
                    pid = "PA-2FE-TX"
                return "LINECARD", name[7:], pid
        elif ((pid.startswith("WS-X64") or pid.startswith("WS-X67")
              or pid.startswith("WS-X65")) and "port" in descr):
            try:
                number = int(name)
            except ValueError:
                number = None
            return "LINECARD", number, pid
        elif ((pid.startswith("WS-SUP") or pid.startswith("VS-S"))
        and "Supervisor Engine" in descr):
            try:
                number = int(name)
            except ValueError:
                number = None
            return "SUP", number, pid
        elif "-DFC" in pid or "-CFC" in pid or "sub-module" in name:
            # DFC subcard
            return "DFC", None, pid
        elif name.startswith("PS "):
            # Power supply
            return "PSU", name.split()[1], pid
        elif name.startswith("Power Supply "):
            return "PSU", name.split()[2], pid
        elif pid.startswith("FAN"):
            # Fan module
            return "FAN", name.split()[1], pid
        elif pid.startswith("NM-"):
            # Network Module
            return "NM", name[-1], pid
        elif pid.endswith("-MB"):
            # Motherboard
            return "MOTHERBOARD", None, pid
        elif "Clock FRU" in descr:
            # Clock module
            return "CLK", name.split()[1], pid
        elif "VTT FRU" in descr:
            # Clock module
            return "VTT", name.split()[1], pid
        # Unknown
        return None, None, None

    def get_transceiver_pid(self, descr):
        match = self.rx_trans.search(descr.upper().replace("-", ""))
        if match:
            return "Unknown | Transceiver | %s" % match.group(1).upper()
        return None

    @NOCScript.match(platform__regex=r"C2960")
    def execute_2960(self):
        objects = self.get_inv()
        objects += self.get_transceivers("show int status")
        return objects

    @NOCScript.match()
    def execute_others(self):
        objects = self.get_inv()
        return objects
