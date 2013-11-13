# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS.get_inventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.lib.validators import is_int


class Script(NOCScript):
    name = "Juniper.JUNOS.get_inventory"
    implements = [IGetInventory]

    rx_chassis = re.compile(
        r"^Chassis\s+(?P<serial>\S+)\s+(?P<rest>.+)$",
        re.IGNORECASE
    )

    rx_part = re.compile(
        r"^\s*(?P<name>\S+(?: \S+)+?)\s+"
        r"(?P<revision>rev \d+|\S{1,6})?\s+"
        r"(?P<part_no>\d{3}-\d{6}|NON-JNPR|BUILTIN)\s+"
        r"(?P<serial>\S+)\s+"
        r"(?P<rest>.+)$", re.IGNORECASE)

    XCVR_MAP = {
        "SFP-T": "NoName | Transceiver | 1G | SFP TX",
        "SFP-SX": "NoName | Transceiver | 1G | SFP SX",
        "SFP-LX10": "NoName | Transceiver | 1G | SFP LX",
        "SFP-LX": "NoName | Transceiver | 1G | SFP LX",
        "XFP-10G-LR": "NoName | Transceiver | 10G | XFP LR",
        "SFP+-10G-LR": "NoName | Transceiver | 10G | SFP+ LR",
        "SFP+-10G-SR": "NoName | Transceiver | 10G | SFP+ SR"
    }

    TYPE_MAP = {
        "CHASSIS": "CHASSIS",
        "PEM": "PEM",
        "ROUTING ENGINE": "RE",
        "CB": "SCB",
        "FPC": "FPC",
        "MPC": "FPC",
        "MIC": "MIC",
        "PIC": "PIC",
        "XCVR": "XCVR"
    }

    def parse_hardware(self, v):
        """
        Parse "show chassis hardware"
        and yeld name, revision, part_no, serial, description
        """
        for l in v.splitlines():
            l = l.strip()
            if not l:
                continue
            match = self.rx_part.search(l)
            if match:
                yield match.groups()
            else:
                match = self.rx_chassis.search(l)
                if match:
                    yield ("Chassis", None, None,
                           match.group("serial"), match.group("rest"))

    def execute(self):
        v = self.cli("show chassis hardware")
        objects = []
        chassis_sn = set()
        for name, revision, part_no, serial, description in self.parse_hardware(v):
            builtin = False
            # Detect type
            t, number = self.get_type(name)
            if not t:
                continue
            # Detect vendor
            if part_no == "NON-JNPR":
                vendor = "NONAME"
            else:
                vendor = "JUNIPER"
            # Get chassis part number from description
            if t == "CHASSIS":
                part_no = description.split()[0].upper()
                chassis_sn.add(serial)
            elif t == "XCVR":
                if vendor == "NONAME":
                    if description == "UNKNOWN":
                        part_no = "NoName | Transceiver | Unknown"
                    else:
                        part_no = self.get_trans_part_no(serial, description)
            elif serial == "BUILTIN" or serial in chassis_sn:
                builtin = True
                part_no = []
            # Submit object
            objects += [{
                "type": t,
                "number": number,
                "vendor": vendor,
                "serial": serial,
                "description": description,
                "part_no": part_no,
                "revision": revision,
                "builtin": builtin
            }]
        return objects

    def get_type(self, name):
        name = name.upper()
        n = name.split()
        if is_int(n[-1]):
            number = n[-1]
            name = " ".join(n[:-1])
        else:
            number = None
        return self.TYPE_MAP.get(name), number

    def get_trans_part_no(self, serial, description):
        """
        Try to detect non-juniper transceiver model
        """
        pn = self.XCVR_MAP.get(description.split()[0])
        if not pn:
            raise Exception("Cannot detect transceiver type: '%s'" % description)
        return pn
