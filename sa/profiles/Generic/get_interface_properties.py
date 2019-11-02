# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Generic.get_interface_properties script
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Dict, Optional, Union, Iterable, Tuple, Callable

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaceproperties import IGetInterfaceProperties
from noc.core.mib import mib
from noc.core.validators import is_mac


class Script(BaseScript):
    name = "Generic.get_interface_properties"
    interface = IGetInterfaceProperties
    MAX_REPETITIONS = 40
    MAX_GETNEXT_RETIRES = 0

    SNMP_NAME_TABLE = "IF-MIB::ifDescr"
    SNMP_MAC_TABLE = "IF-MIB::ifPhysAddress"
    SNMP_ADMIN_STATUS_TABLE = "IF-MIB::ifAdminStatus"
    SNMP_OPER_STATUS_TABLE = "IF-MIB::ifOperStatus"

    def execute_snmp(
        self,
        interface=None,
        enable_ifindex=False,
        enable_interface_mac=False,
        enable_admin_status=False,
        enable_oper_status=False,
    ):
        iter_tables = []
        ifindex = None
        if interface:
            ifindex = self.get_interface_ifindex(interface)
            iter_tables += [self.iter_interface_ifindex(interface, ifindex)]
        else:
            iter_tables += [self.iter_iftable("name", mib[self.SNMP_NAME_TABLE])]
        if enable_interface_mac:
            iter_tables += [self.iter_iftable("mac", mib[self.SNMP_MAC_TABLE], ifindex=ifindex)]
        if enable_admin_status:
            iter_tables += [
                self.iter_iftable(
                    "admin_status",
                    mib[self.SNMP_ADMIN_STATUS_TABLE],
                    ifindex=ifindex,
                    clean=self.clean_status,
                )
            ]
        if enable_oper_status:
            iter_tables += [
                self.iter_iftable(
                    "oper_status",
                    mib[self.SNMP_OPER_STATUS_TABLE],
                    ifindex=ifindex,
                    clean=self.clean_status,
                )
            ]
        # Collect and merge results
        data = self.merge_tables(*tuple(iter_tables))
        # Format result
        result = []
        for ifindex in sorted(data):
            v = data[ifindex]
            if "name" not in v:
                continue
            item = {"interface": v["name"]}
            if enable_ifindex and "ifindex" in v:
                item["ifindex"] = v["ifindex"]
            if enable_interface_mac and "mac" in v and is_mac(v["mac"]):
                item["mac"] = v["mac"]
            if enable_admin_status and "admin_status" in v:
                item["admin_status"] = v["admin_status"]
            if enable_oper_status and "oper_status" in v:
                item["oper_status"] = v["oper_status"]
            result += [item]
        return result

    def merge_tables(self, *args):
        # type: (Optional[Iterable]) -> Dict[int,Dict[str, Union[int, bool, str]]]
        """
        Merge iterables into single table

        :param args:
        :return:
        """
        r = {}
        for iter_table in args:
            for key, ifindex, value in iter_table:
                if ifindex not in r:
                    r[ifindex] = {"ifindex": ifindex}
                r[ifindex][key] = value
        return r

    @staticmethod
    def clean_default(v):
        return v

    @staticmethod
    def clean_status(v):
        return v == 1

    def clean_ifname(self, v):
        return self.profile.convert_interface_name(v)

    def iter_iftable(self, key, oid, ifindex=None, clean=None):
        # type: (str, str, Optional[int], Callable) -> Iterable[Tuple[str, Union[str, int]]]
        """
        Collect part of IF-MIB table.

        :param oid: Base oid, either in numeric or symbolic form
        :param ifindex: Collect information for single interface only, if set
        :param clean: Cleaning function
        :return:
        """
        clean = clean or self.clean_default
        if "::" in oid:
            oid = mib[oid]
        if ifindex:
            # Single interface
            v = self.snmp.get("%s.%s" % (oid, ifindex))
            try:
                yield key, ifindex, clean(v)
            except ValueError:
                pass
        else:
            # All interfaces
            for r_oid, v in self.snmp.getnext(
                oid,
                max_repetitions=self.get_max_repetitions(),
                max_retries=self.get_getnext_retires(),
            ):
                try:
                    yield key, int(r_oid.rsplit(".", 1)[1]), clean(v)
                except ValueError:
                    pass

    def get_max_repetitions(self):
        return self.MAX_REPETITIONS

    def get_getnext_retires(self):
        return self.MAX_GETNEXT_RETIRES

    def get_interface_ifindex(self, name):
        # type: (str) -> int
        """
        Get ifindex for given interface
        :param name:
        :return:
        """
        for r_oid, v in self.snmp.getnext(
            mib[self.SNMP_NAME_TABLE],
            max_repetitions=self.get_max_repetitions(),
            max_retries=self.get_getnext_retires(),
        ):
            if self.profile.convert_interface_name(v) == name:
                return int(r_oid.rsplit(".", 1)[1])
        raise KeyError

    def iter_interface_ifindex(self, name, ifindex):
        yield "name", ifindex, self.profile.convert_interface_name(name)
