# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.SCOS.get_inventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(NOCScript):
    name = "Cisco.SCOS.get_inventory"
    implements = [IGetInventory]

    rx_item = re.compile(
        r"^NAME: \"(?P<name>[^\"]+)\", DESCR: \"(?P<descr>[^\"]+)\"\s*\n"
        r"PID:\s+(?P<pid>\S+)?\s*,\s+VID:\s+"
        r"(?P<vid>\S+[^\,]+)?\s*, SN: (?P<serial>\S+)",
        re.MULTILINE | re.DOTALL
    )

    def execute(self):
        objects = []
        v = self.cli("show inventory raw")
        for match in self.rx_item.finditer(v):
            vendor = None
            #Internal containers, bays, links, ports, processors
            #Not needed
            if match.group("pid") == '""':
                continue
            type, number, part_no = self.get_type(
                match.group("name"), match.group("pid"),
                match.group("descr"), len(objects)
            )
            serial = match.group("serial")
            descr = match.group("descr")
            vid = match.group("vid")
            pid = match.group("pid")
            # If not part_no for transceiver
            if type == "XCVR":
                if part_no == "N/A":
                    if self.rx_trans.search(pid):
                        part_no = self.get_transceiver_pid(pid)
                    else:
                        part_no = pid

            if not part_no:
                print "!!! UNKNOWN: ", match.groupdict()
                continue
            else:
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
                    "description": descr.strip(),
                    "part_no": [part_no],
                    "revision": vid,
                    "builtin": False
                }]

        # Sort transceivers
        r = []
        t = {}
        for i in objects:
            if "XCVR" in i.get("type"):
                continue
            elif "SPA" in i.get("type"):
                for p in objects:
                    if ("XCVR" in p.get("type") and
                        i.get("number") == p.get("number").split("/")[1]):
                           t = p.copy()
                           t["number"] = p.get("number").split("/")[2]
                           r += [i]
                           r += [t]
            else:
                r += [i]

        return r


    def get_type(self, name, pid, descr, lo):
        """
        Get type, number and part_no
        """
        if pid is None:
            pid = ""
        if (pid.startswith("XFP") or
                pid.startswith("SFP")):
            # Transceivers
            # Get number
            if name.startswith("SCE8000 optic"):
                # Get port number
                number = name.split(" ")[-1]
            else:
                number = None
            if pid in ("", "N/A", "Unspecified"):
                return "XCVR", number, "N/A"
            else:
                return "XCVR", number, pid
        elif lo == 0 and "CHASSIS" in name.upper():
            return "CHASSIS", None, pid
        elif "SCM" in name:
            # Service Control Module
            try:
                number = int(name.split()[-1])
            except ValueError:
                number = None
            return "SCM", number, pid
        elif "SIP" in name:
            # Interface card
            try:
                number = int(name.split()[-1])
            except ValueError:
                number = None
            return "SIP", number, pid
        elif "SPA-" in pid:
            # SPA subcard
            try:
                number = name.split("/")[-1]
            except ValueError:
                number = None
            return "SPA", number, pid
        elif pid.startswith("PWR-"):
            # Power supply
            return "PSU", name.split()[-1], pid
        elif "FAN" in name:
            # Fan module
            return "FAN", name.split()[-1], pid
        # Unknown
        return None, None, None