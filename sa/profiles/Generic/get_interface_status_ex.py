# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Generic.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import six

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx
from noc.sa.interfaces.base import InterfaceTypeError
from noc.core.mib import mib


class Script(BaseScript):
    name = "Generic.get_interface_status_ex"
    interface = IGetInterfaceStatusEx
    requires = []
    HIGH_SPEED = 4294967295
    MAX_REPETITIONS = 40
    MAX_GETNEXT_RETIRES = 0
    IFNAME_OID = "IF-MIB::ifName"

    def get_max_repetitions(self):
        return self.MAX_REPETITIONS

    def get_getnext_retires(self):
        return self.MAX_GETNEXT_RETIRES

    def get_snmp_ifstatus_get_timeout(self):
        """
        Timeout for snmp GET request
        :return:
        """
        return self.profile.snmp_ifstatus_get_timeout

    def get_snmp_ifstatus_get_chunk(self):
        """
        Aggregate up to *snmp_metrics_get_chunk* oids
        to one SNMP GET request
        :return:
        """
        return self.profile.snmp_ifstatus_get_chunk

    def get_ifname_oid(self):
        """
        OID return interface name
        :return:
        """
        return self.IFNAME_OID

    def get_iftable(self, oid, ifindex=None):
        """
        If ifindex - collect information on the given interfaces
        Else - collect information for all interfaces
        :return:
        """
        if "::" in oid:
            oid = mib[oid]
        if ifindex:
            results = self.snmp.get_chunked(
                oids=["%s.%s" % (oid, i) for i in ifindex],
                chunk_size=self.get_snmp_ifstatus_get_chunk(),
                timeout_limits=self.get_snmp_ifstatus_get_timeout(),
            )
            for k, v in six.iteritems(results):
                yield int(k.split(".")[-1]), v
        else:
            for oid, v in self.snmp.getnext(
                oid,
                max_repetitions=self.get_max_repetitions(),
                max_retries=self.get_getnext_retires(),
            ):
                yield int(oid.rsplit(".", 1)[-1]), v

    def apply_table(self, r, mib, name, f=None):
        f = f or (lambda x: x)
        for ifindex, v in self.get_iftable(mib, list(r)):
            s = r.get(ifindex)
            if s:
                s[name] = f(v)

    def get_data(self, interfaces=None):
        # ifIndex -> ifName mapping
        r = {}  # ifindex -> data
        unknown_interfaces = []
        if interfaces:
            for i in interfaces:
                r[i["ifindex"]] = {"interface": i["interface"]}
        else:
            for ifindex, name in self.get_iftable(self.get_ifname_oid()):
                try:
                    v = self.profile.convert_interface_name(name)
                except InterfaceTypeError as e:
                    self.logger.debug("Ignoring unknown interface %s: %s", name, e)
                    unknown_interfaces += [name]
                    continue
                r[ifindex] = {"interface": v}
        if_index = list(r)
        # Apply ifAdminStatus
        self.apply_table(
            r, "IF-MIB::ifAdminStatus", "admin_status", lambda x: x == 1 if x is not None else None
        )
        # Apply ifOperStatus
        self.apply_table(
            r, "IF-MIB::ifOperStatus", "oper_status", lambda x: x == 1 if x is not None else None
        )
        # Apply dot3StatsDuplexStatus
        self.apply_table(
            r,
            "EtherLike-MIB::dot3StatsDuplexStatus",
            "full_duplex",
            lambda x: x != 2 if x is not None else None,
        )
        # Apply ifSpeed
        highspeed = set()
        for ifindex, s in self.get_iftable("IF-MIB::ifSpeed", if_index):
            ri = r.get(ifindex)
            if ri and s is not None:
                # s is None if OID is not exists
                if self.is_high_speed(ri, s):
                    highspeed.add(ifindex)
                elif s:
                    r[ifindex]["in_speed"] = s // 1000
                    r[ifindex]["out_speed"] = s // 1000
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
        return list(six.itervalues(r))

    def is_high_speed(self, data, speed):
        """
        Detect should we check ifHighSpeed
        :param data: dict with
        :param speed:
        :return:
        """
        return speed == self.HIGH_SPEED

    def execute_snmp(self, interfaces=None, **kwargs):
        r = self.get_data(interfaces=interfaces)
        return r
