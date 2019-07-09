# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Ericsson.SEOS.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import six

# NOC modules
from noc.sa.profiles.Generic.get_interface_status_ex import Script as BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx
from noc.sa.interfaces.base import InterfaceTypeError
from noc.core.mib import mib


class Script(BaseScript):
    name = "Ericsson.SEOS.get_interface_status_ex"
    interface = IGetInterfaceStatusEx
    requires = []

    def get_data(self, interfaces=None):
        # ifIndex -> ifName mapping
        r = {}  # ifindex -> data
        radio = {}
        res = {}
        unknown_interfaces = []
        if interfaces:
            for i in interfaces:
                if "." in i["interface"]:
                    radio[i["ifindex"]] = {"interface": i["interface"]}
                else:
                    r[i["ifindex"]] = {"interface": i["interface"]}
        else:
            for ifindex, name in self.get_iftable("IF-MIB::ifName"):
                descr = self.snmp.get(mib["IF-MIB::ifDescr", ifindex])
                try:
                    v = self.profile.convert_interface_name("%s/%s" % (name, descr))
                except InterfaceTypeError as e:
                    self.logger.debug(
                        "Ignoring unknown interface %s: %s", "%s/%s" % (name, descr), e
                    )
                    unknown_interfaces += [name]
                    continue
                if "." in v:
                    radio[ifindex] = {"interface": v}
                else:
                    r[ifindex] = {"interface": v}
        if_index = list(r)
        # Apply ifAdminStatus
        self.apply_table(r, "IF-MIB::ifAdminStatus", "admin_status", lambda x: x == 1)
        # Apply ifOperStatus
        self.apply_table(r, "IF-MIB::ifOperStatus", "oper_status", lambda x: x == 1)
        # Apply Radio ifAdminStatus
        self.apply_table(
            radio, "1.3.6.1.4.1.193.81.3.4.3.1.2.1.8", "admin_status", lambda x: x == 3
        )
        # Apply Radio ifOperStatus
        self.apply_table(radio, "1.3.6.1.4.1.193.81.3.4.3.1.2.1.7", "oper_status", lambda x: x == 3)
        # Apply dot3StatsDuplexStatus
        self.apply_table(r, "EtherLike-MIB::dot3StatsDuplexStatus", "full_duplex", lambda x: x != 2)
        # Apply ifSpeed
        highspeed = set()
        for ifindex, s in self.get_iftable("IF-MIB::ifSpeed", if_index):
            ri = r.get(ifindex)
            if ri and s is not None:
                # s is None if OID is not exists
                if self.is_high_speed(ri, s):
                    highspeed.add(ifindex)
                elif s:
                    ri["in_speed"] = s // 1000
                    ri["out_speed"] = s // 1000
        # Refer to ifHighSpeed if necessary
        if highspeed:
            for ifindex, s in self.get_iftable("IF-MIB::ifHighSpeed", if_index):
                if ifindex in highspeed and s is not None:  # s is None if OID is not exists
                    s = int(s)
                    if s:
                        r[ifindex]["in_speed"] = s * 1000
                        r[ifindex]["out_speed"] = s * 1000
        # Log unknown interfaces
        if unknown_interfaces:
            self.logger.info("%d unknown interfaces has been ignored", len(unknown_interfaces))
        for ifindex, rr in six.iteritems(radio):
            rr["in_speed"] = self.snmp.get("1.3.6.1.4.1.193.81.3.4.1.1.14.1.7.1")
            rr["out_speed"] = self.snmp.get("1.3.6.1.4.1.193.81.3.4.1.1.14.1.7.1")
            res[ifindex] = rr
        r.update(res)
        return list(six.itervalues(r))
