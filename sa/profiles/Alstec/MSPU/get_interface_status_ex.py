# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.MSPU.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import six

# NOC modules
from noc.sa.profiles.Generic.get_interface_status_ex import Script as BaseScript
from noc.sa.interfaces.base import InterfaceTypeError


class Script(BaseScript):
    name = "Alstec.MSPU.get_interface_status_ex"

    def get_data(self, interfaces=None):
        # ifIndex -> ifName mapping
        r = {}  # ifindex -> data
        unknown_interfaces = []
        if interfaces:
            for i in interfaces:
                r[i["ifindex"]] = {"interface": i["interface"]}
        else:
            for ifindex, name in self.get_iftable("IF-MIB::ifName"):
                try:
                    v = self.profile.convert_interface_name(name)
                except InterfaceTypeError as e:
                    self.logger.debug("Ignoring unknown interface %s: %s", name, e)
                    unknown_interfaces += [name]
                    continue
                r[ifindex] = {"interface": v}
        if_index = list(r)
        # Apply ifAdminStatus
        self.apply_table(r, "IF-MIB::ifAdminStatus", "admin_status", lambda x: x == 1)
        # Apply ifOperStatus
        self.apply_table(r, "IF-MIB::ifOperStatus", "oper_status", lambda x: x == 1)
        # Apply dot3StatsDuplexStatus
        self.apply_table(r, "EtherLike-MIB::dot3StatsDuplexStatus", "full_duplex", lambda x: x != 2)
        # Apply ifSpeed
        for ifindex, s in self.get_iftable("IF-MIB::ifSpeed", if_index):
            ri = r.get(ifindex)
            if ri and "uplink" in ri["interface"]:
                s = int(s)
                ri["in_speed"] = s
                ri["out_speed"] = s
            elif ri and ri["interface"].startswith("h"):
                s = int(s)
                ri["in_speed"] = s // 1000
                ri["out_speed"] = s // 1000
            elif ri:
                s = int(s)
                ri["in_speed"] = s // 10
                ri["out_speed"] = s // 10

        return list(six.itervalues(r))
