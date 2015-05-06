# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.NXOS.get_inventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.sa.interfaces.base import InterfaceTypeError


class Script(NOCScript):
    name = "Cisco.NXOS.get_inventory"
    implements = [IGetInventory]

    rx_item = re.compile(
        r"^NAME: \"(?P<name>[^\"]+)\", DESCR: \"(?P<descr>[^\"]+)\"\n"
        r"PID:\s+(?P<pid>\S*)\s*,\s+VID:\s+(?P<vid>\S*)\s*, SN: (?P<serial>\S+)",
        re.MULTILINE | re.DOTALL
    )

    rx_sfp = re.compile(
        r"^(?P<number>Ethernet\d+(/\d+)*)\n\s+transceiver is present\n"
        r"\s+type is(\s(?P<type>\S+[ \S+]*))?\n\s+name is\s(?P<vendor>\S+[ \S+]*)\n"
        r"\s+part number is\s(?P<partno>\S+)\n\s+revision is\s(?P<rev>\S+)\n"
        r"\s+serial number is\s(?P<serial>\S+)\n",
        re.MULTILINE | re.DOTALL
    )

    rx_trans = re.compile("((?:100|1000|10G)BASE\S+)")

    # set of pids GEM modules w/o transceivers
    gem_w_o_sfp = set([
        "N55-M160L3",
        "N55-M160L3-V2"
    ])

    def execute(self):
        objects = []
        trans = []
        v = self.cli("show inventory | no-more")
        s = self.cli("sh int transceiver | no-more")

        #get transceivers
        for match in self.rx_sfp.finditer(s):
            if match.group("number").startswith("Ethernet"):
                if match.group("type"):
                    if ("Fabric" in match.group("type") or
                        "BASE" in match.group("type").upper()):
                        parts = [match.group("partno")]
                    elif "BASE" in match.group("partno").upper():
                        parts = [match.group("type")]
                    else:    
                        parts = [match.group("partno"), match.group("type")]
                else:
                    parts = [match.group("partno")]
                trans += [{
                    "type": "XCVR",
                    "number": self.get_xcvr_num(match.group("number")),
                    "vendor": self.get_vendor(match.group("vendor")),
                    "serial": match.group("serial"),
                    "description": match.group("type"),
                    "part_no": parts,
                    "revision": match.group("rev"),
                    "builtin": False
                }]

        for match in self.rx_item.finditer(v):
            type, number, part_no = self.get_type(
                match.group("name"), match.group("pid"),
                match.group("descr"), len(objects)
            )
            builtin = False
            serial = [match.group("serial"), None]["N/A" in match.group("serial")]
            rev = [match.group("vid"), None]["N/A" in match.group("vid")]
            if not part_no:
                print "!!! UNKNOWN: ", match.groupdict()
                continue
            else:
                vendor = "CISCO" if "NoName" not in part_no else "NONAME"
                objects += [{
                    "type": type,
                    "number": number,
                    "vendor": vendor,
                    "serial": serial,
                    "description": match.group("descr"),
                    "part_no": [part_no],
                    "revision": rev,
                    "builtin": builtin
                }]
                # Add transceivers
                if (objects[-1]["type"] == "SUP" or 
                    (objects[-1]["type"] == "GEM" and
                     objects[-1]["part_no"][0] not in self.gem_w_o_sfp)):

                    # Get number of last chassis
                    for c in objects:
                        if c["type"] == "CHASSIS":
                            number_c = c["number"]

                    for i in trans:
                        t = dict(i)
                        # check number of chassis and module
                        if not number_c:
                            if (len(t["number"].split("/")) == 2):
                                if t["number"].split("/")[0] == number:
                                    objects += [t]
                                    # rewrite number
                                    objects[-1]["number"] = objects[-1]["number"].split("/")[-1]
                        else:
                            if int(t["number"].split("/")[0]) == int(number_c):
                                if int(t["number"].split("/")[1]) == int(number):
                                    objects += [t]
                                    objects[-1]["number"] = objects[-1]["number"].split("/")[-1]
        return objects

    def get_type(self, name, pid, descr, lo):
        """
        Get type, number and part_no
        """
        if "CHASSIS" in name.upper():
            try:
                number = int(name.split()[1])
            except:
                number = None
            return "CHASSIS", number, pid
        elif "GEM" in descr:
            number = name.split()[-1]
            return "GEM", number, pid
        elif "Superv" in descr:
            number = name.split()[-1]
            return "SUP", number, pid + "-SUP"
        elif "XFP" in pid or "GLC" in pid or "SFP" in descr:
            number = name.split()[2].split("/")[-1]
            if not pid:
                pid = self.get_transceiver_pid(descr)
                if not pid:
                    return None, None, None
            return "XCVR", number, pid
        elif "FAN" in pid:
            number = name.split()[-1]
            return "FAN", number, pid
        elif "power supply" in name.lower():
            number = name.split()[-1]
            return "PSU", number, pid
        # Unknown
        return None, None, None

    def get_vendor(self, vendor):
        if vendor.upper().startswith("CISCO-"):
            return vendor[6:].upper()
        else:
            return vendor.split()[0].upper()

    def get_xcvr_num(self, number):
        if number.startswith("Ethernet"):
            return number[8:]
        else:
            return number

    def get_transceiver_pid(self, descr):
        match = self.rx_trans.search(descr)
        if match:
            return "Unknown | Transceiver | %s" % match.group(1).upper()
        return "Unknown | Transceiver | Unknown"
