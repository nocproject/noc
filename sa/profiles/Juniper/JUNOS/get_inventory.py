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


class Script(NOCScript):
    name = "Juniper.JUNOS.get_inventory"
    implements = [IGetInventory]

    JUNIPER = "JUNIPER"
    NONAME = "NONAME"

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

    T_MAP = {
        "SFP-T": "NoName | Transceiver | 1G | SFP TX",
        "SFP-LX10": "NoName | Transceiver | 1G | SFP LX",
        "SFP-LX": "NoName | Transceiver | 1G | SFP LX",
        "XFP-10G-LR": "NoName | Transceiver | 10G | XFP LR",
        "SFP+-10G-LR": "NoName | Transceiver | 10G | SFP+ LR"
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
        def get_object(objects, omap, name, revision,
                       part_no, serial, description, vendor=None):
            o = {
                "id": len(objects),
                "vendor": vendor or self.JUNIPER,
                "serial": serial,
                "description": description,
                "part_no": [part_no],
                "connections": []
            }
            if revision:
                o["revision"] = revision
            objects += [o]
            omap[name.lower()] = o
            return o

        def connect(object, name, remote_object, remote_name):
            object["connections"] += [{
                "name": name,
                "object": remote_object["id"],
                "remote_name": remote_name
            }]

        v = self.cli("show chassis hardware")
        objects = []
        omap = {}
        chassis = None
        chassis_type = None
        for name, revision, part_no, serial, description in self.parse_hardware(v):
            if name.lower() == "chassis":
                # New object
                chassis_type = description.split()[0].upper()
                chassis = {
                    "id": len(objects),
                    "vendor": self.JUNIPER,
                    "serial": serial,
                    "description": description,
                    "part_no": [chassis_type],
                    "connections": []
                }
                objects += [chassis]
                omap = {}
                fpc = None
                mic = None
                co = None
                nfpc = None
                npic = None
                mnpic = None
            elif chassis is None:
                continue  # Bug
            else:
                # Chassis module
                n = name.lower()
                if n.startswith("pem "):
                    # Power modules
                    o = get_object(objects, omap,
                                   name, revision, part_no,
                                   serial, description)
                    cn = n.replace(" ", "")
                    connect(chassis, cn, o, "in")
                elif n.startswith("routing engine"):
                    # RE modules
                    o = get_object(objects, omap,
                                   name, revision, part_no,
                                   serial, description)
                    # Will be connected at scb
                    # for mx series
                elif n.startswith("cb "):
                    # SCB
                    o = get_object(objects, omap,
                                   name, revision, part_no,
                                   serial, description)
                    n = name.split()[-1]
                    cn = "scb%s" % n
                    connect(chassis, cn, o, "in")
                    #
                    if chassis_type.startswith("MX"):
                        r = omap.get("routing engine %s" % n)
                        if r:
                            connect(o, "re", r, "in")
                elif n.startswith("fpc "):
                    # Line card
                    nfpc = name.split()[-1]
                    o = get_object(objects, omap,
                                   name, revision, part_no,
                                   serial, description)
                    cn = "fpc%s" % nfpc
                    connect(chassis, cn, o, "in")
                    fpc = o
                    co = o
                    npic = None
                    mic = None
                    mnpic = None
                elif n.startswith("mic "):
                    nmic = n.split()[-1]
                    mnpic = -1
                    if serial != "BUILTIN":
                        o = get_object(objects, omap,
                                       name, revision, part_no,
                                       serial, description)
                        cn = "mic%s" % nmic
                        connect(fpc, cn, o, "in")
                        co = o
                        mic = o
                elif n.startswith("pic "):
                    npic = n.split()[-1]
                    if mic:
                        if mnpic is not None:
                            mnpic += 1
                    if serial != "BUILTIN":
                        o = get_object(objects, omap,
                                       name, revision, part_no,
                                       serial, description)
                        cn = "pic%s" % npic
                        connect(fpc, cn, o, "in")
                        co = o
                elif n.startswith("xcvr "):
                    # Transceiver
                    if co == fpc:
                        # Builtin pic
                        cn = "%s/%s" % (npic, name.split()[-1])
                    elif co == mic:
                        # MIC
                        cn = "%s/%s" % (mnpic, name.split()[-1])
                    else:
                        # Separate PIC
                        cn = name.split()[-1]
                    vendor = self.JUNIPER
                    if part_no == "NON-JNPR":
                        vendor = self.NONAME
                        # Try to detect transceiver type
                        if description == "UNKNOWN":
                            part_no = "NoName | Transceiver | Unknown"
                        else:
                            part_no = self.get_trans_part_no(serial, description)
                    o = get_object(objects, omap,
                                   name, revision, part_no,
                                   serial, description, vendor=vendor)
                    connect(co, cn, o, "in")
        return objects

    def get_trans_part_no(self, serial, description):
        """
        Try to detect non-juniper transceiver model
        """
        pn = self.T_MAP.get(description.split()[0])
        if not pn:
            raise Exception("Cannot detect transceiver type: '%s'" % description)
        return pn
