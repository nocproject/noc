# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES.get_inventory
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
    name = "EdgeCore.ES.get_inventory"
    implements = [IGetInventory]

    rx_trans_no = re.compile(
        r"\s+(?P<number>\d/\d+)\n")
    rx_trans_vend = re.compile(
        r"\s+Vendor Name\s+:\s+(?P<vend>\S+)\n")
    rx_trans_pid = re.compile(
        r"\s+Vendor PN\s+:\s+(?P<pid>\S+)\n")
    rx_trans_rev = re.compile(
        r"\s+Vendor Rev\s+:\s+(?P<rev>\S+)\n")
    rx_trans_sn = re.compile(
        r"\s+Vendor SN\s+:\s+(?P<sn>\S+)\n")
    rx_trans = re.compile("((?:100|1000)BASE\s+SFP)")

    rx_int_type = re.compile(
        r"(?P<int>Eth\s+\d/\d+)\n\s+Basic Information:\s+\n"
        r"\s+Port Type:\s+(?P<type>\S+[\S ]*)\n",
        re.IGNORECASE | re.MULTILINE | re.DOTALL
    )

    def execute(self):
        objects = []
        #Chassis info
        p = self.scripts.get_version()
        objects += [{
            "type": "CHASSIS",
            "number": None,
            "vendor": "EDGECORE",
            "serial": p["attributes"].get("Serial Number"),
            "description": p["vendor"] + " " + p["platform"],
            "part_no": [p["platform"]],
            "revision": p["attributes"].get("HW version"),
            "builtin": False
        }]

        #Detect transceivers
        iface = self.cli("sh int status")
        for i in self.rx_int_type.finditer(iface):
            if "SFP" not in i.group("type"):
                continue
            else:
                try:
                    v = self.cli("show int trans " + i.group("int"))
                    for t in v.split("Ethernet"):
                        pid = ""
                        #Parsing
                        match = self.rx_trans_no.search(t)
                        if match:
                            number = match.group("number")
                            match = self.rx_trans_pid.search(t)
                            pid = match.group("pid").strip() if match else ""
                            match = self.rx_trans_vend.search(t)
                            vendor = match.group("vend").strip() if match else "NONAME"
                            match = self.rx_trans_rev.search(t)
                            revision = match.group("rev").strip() if match else None
                            match = self.rx_trans_sn.search(t)
                            serial = match.group("sn").strip() if match else None
                            #Noname transceiver
                            if (pid in ("", "N/A", "Unspecified") or
                                "\\x" in repr(pid).strip("'") or
                                "NONAME" in vendor):
                                   pid = self.get_transceiver_pid(i.group("type").upper())
                            if not pid:
                                print "!!! UNKNOWN SFP: Eth", number
                                continue
                            else:
                                # Add transceiver
                                objects += [{
                                    "type": "XCVR",
                                    "number": i.group("int").split("/")[-1],
                                    "vendor": vendor,
                                    "serial": unicode(repr(serial), "utf-8").strip("'"),
                                    "description": "SFP Transceiver",
                                    "part_no": [pid],
                                    "revision": unicode(repr(revision), "utf-8").strip("'"),
                                    "builtin": False
                                }]

                except self.CLISyntaxError:
                    print "show transceiver command not supported"
                    pid = self.get_transceiver_pid(i.group("type").upper())
                    if not pid:
                        print "!!! UNKNOWN SFP: ", i.group("int")
                        continue
                    else:
                        # Add transceiver
                        objects += [{
                            "type": "XCVR",
                            "number": i.group("int").split("/")[-1],
                            "vendor": "NONAME",
                            "serial": None,
                            "description": "SFP Transceiver",
                            "part_no": [pid],
                            "revision": None,
                            "builtin": False
                        }]
                    pass

        return objects

    def get_transceiver_pid(self, type):
        match = self.rx_trans.search(type)
        if match:
            if "1000" in match.group(1):
                return "NoName | Transceiver | 1G | SFP"
            return "NoName | Transceiver | 100M | SFP"
        return None
