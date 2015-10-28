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
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.lib.validators import is_int


class Script(BaseScript):
    name = "Juniper.JUNOS.get_inventory"
    interface = IGetInventory

    UNKNOWN_XCVR = "NoName | Transceiver | Unknown"

    rx_chassis = re.compile(
        r"^Chassis\s+(?P<revision>REV \d+)?\s+(?P<serial>\S+)\s+(?P<rest>.+)$",
        re.IGNORECASE
    )

    rx_part = re.compile(
        r"^\s*(?P<name>\S+(?: \S+)+?)\s+"
        r"(?P<revision>rev \d+|\S{1,6})?\s+"
        r"(?P<part_no>\d{3}-\d{6}|NON-JNPR|BUILTIN)\s+"
        r"(?P<serial>\S+)\s+"
        r"(?P<rest>.+)$", re.IGNORECASE)

    TYPE_MAP = {
        "CHASSIS": "CHASSIS",
        "PEM": "PEM",
        "POWER SUPPLY": "PEM",
        "PSU": "PSU",
        "ROUTING ENGINE": "RE",
        "CB": "SCB",
        "FPC": "FPC",
        "MPC": "FPC",
        "MIC": "MIC",
        "PIC": "PIC",
        "XCVR": "XCVR",
        "FTC": "FAN",
        "FAN TRAY": "FAN"
    }

    IGNORED = {
        "RE": set([
            "750-033065",  # EX4200-24T, 8 POE
            "750-021258",  # EX4200-24F
            "750-034594",  # RE-SRX210HE
            "710-017560",  # 710-017560
            "750-021778",  # RE-SRX210B
            "710-015273",  # RE-J4350-2540
            "710-017560"   # RE-J2320-2000
        ])
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
            if l.startswith("node"):
                self.chassis_no = l.strip()[4:-1]
                continue
            match = self.rx_part.search(l)
            if match:
                yield match.groups()
            else:
                match = self.rx_chassis.search(l)
                if match:
                    rev = match.group("revision")
                    yield ("Chassis", rev, None,
                           match.group("serial"), match.group("rest"))

    def execute(self):
        self.chassis_no = None
        v = self.cli("show chassis hardware")
        objects = []
        chassis_sn = set()
        for name, revision, part_no, serial, description in self.parse_hardware(v):
            builtin = False
            # Detect type
            t, number = self.get_type(name)
            if not t:
                self.logger.error("Unknown module: %s %s %s %s %s",
                                  name, revision, part_no,
                                  serial, description)
                continue
            # Discard virtual chassis and ignored part numbers
            if description == "Virtual Chassis":
                continue
            if t in self.IGNORED and part_no in self.IGNORED[t]:
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
            elif t == "FPC":
                if description.startswith("EX4"):
                    t = "CHASSIS"
                    chassis_sn.add(serial)
            elif t == "XCVR":
                if vendor == "NONAME":
                    if description in ("UNKNOWN", "UNSUPPORTED"):
                        part_no = self.UNKNOWN_XCVR
                    else:
                        part_no = self.get_trans_part_no(serial, description)
            elif serial == "BUILTIN" or serial in chassis_sn:
                builtin = True
                part_no = []
            if t == "CHASSIS" and number is None and self.chassis_no is not None:
                number = self.chassis_no
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
        n = description.split()[0].split("-")
        if len(n) == 2:
            # SFP-LX
            t, m = n
            s = "1G"
            if m == "LX10":
                m = "LX"
        elif len(n) == 3:
            # SFP+-10G-LR
            t, s, m = n
        else:
            self.error("Cannot detect transceiver type: '%s'" % description)
            return self.UNKNOWN_XCVR
        return "NoName | Transceiver | %s | %s %s" % (s, t, m)
