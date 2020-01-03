# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MES.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# Third-party modules
import six
from six.moves import zip

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.core.validators import is_int, is_ipv4, is_ipv6, is_mac
from noc.core.mac import MAC
from noc.core.mib import mib
from noc.core.lldp import (
    LLDP_CHASSIS_SUBTYPE_MAC,
    LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
    LLDP_CHASSIS_SUBTYPE_LOCAL,
    LLDP_PORT_SUBTYPE_ALIAS,
    LLDP_PORT_SUBTYPE_COMPONENT,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NETWORK_ADDRESS,
    LLDP_PORT_SUBTYPE_LOCAL,
    LLDP_CAP_OTHER,
    LLDP_CAP_REPEATER,
    LLDP_CAP_BRIDGE,
    LLDP_CAP_WLAN_ACCESS_POINT,
    LLDP_CAP_ROUTER,
    LLDP_CAP_TELEPHONE,
    LLDP_CAP_DOCSIS_CABLE_DEVICE,
    LLDP_CAP_STATION_ONLY,
    lldp_caps_to_bits,
)
from noc.core.comp import smart_text


class Script(BaseScript):
    name = "Eltex.MES.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_detail = re.compile(
        r"^Device ID: (?P<dev_id>\S+)\s*\n"
        r"^Port ID: (?P<port_id>\S+)\s*\n"
        r"^Capabilities:(?P<caps>.*)\n"
        r"^System Name:(?P<sys_name>.*)\n"
        r"^System description:(?P<sys_descr>(?:.*\n)*?)"
        r"^Port description:(?P<port_descr>.*)\n",
        re.MULTILINE,
    )

    rx_header_start = re.compile(r"^\s*[-=]+[\s\+]+[-=]+")
    rx_col = re.compile(r"^([\s\+]*)([\-]+|[=]+)")

    def parse_table(
        self,
        s,
        allow_wrap=False,
        allow_extend=False,
        expand_columns=False,
        max_width=0,
        footer=None,
        n_row_delim="",
        expand_tabs=True,
        strip_rows=False,
    ):
        """
        Parse string containing table an return a list of table rows.
        Each row is a list of cells.
        Columns are determined by a sequences of ---- or ==== which are
        determines rows bounds.
        Examples:
        First Second Third
        ----- ------ -----
        a     b       c
        ddd   eee     fff
        Will be parsed down to the [["a","b","c"],["ddd","eee","fff"]]

        :param s: Table for parsing
        :type s: str
        :param allow_wrap: Union if cell contins multiple line
        :type allow_wrap: bool
        :param allow_extend: Check if column on row longest then column width, enlarge it and shift rest of columns
        :type allow_extend: bool
        :param expand_columns: Expand columns covering all available width
        :type expand_columns: bool
        :param max_width: Max table width, if table width < max_width extend length, else - nothing
        :type max_width: int
        :param footer: stop iteration if match expression footer
        :type footer: string
        :param n_row_delim: Append delimiter to next cell line
        :type n_row_delim: string
        :param expand_tabs: Apply expandtabs() to each line
        :type expand_tabs: bool
        :param strip_rows: Apply strip() to rest rows in column, if allow_wrap set to True
        :type strip_rows: bool
        """
        r = []
        columns = []
        if footer is not None:
            rx_footer = re.compile(footer)
        for line in s.splitlines():
            if expand_tabs:
                # Replace tabs with spaces with step 8
                line = line.expandtabs()
            if not line.strip() and footer is None:
                columns = []
                continue
            if footer is not None and rx_footer.search(line):
                break  # Footer reached, stop
            if not columns and self.rx_header_start.match(line):
                # Column delimiters found. try to determine column's width
                columns = []
                x = 0
                while line:
                    match = self.rx_col.match(line)
                    if not match:
                        break
                    spaces = len(match.group(1))
                    dashes = len(match.group(2))
                    columns += [(x + spaces, x + spaces + dashes)]
                    x += match.end()
                    line = line[match.end() :]
                if max_width and columns[-1][-1] < max_width:
                    columns[-1] = (columns[-1][0], max_width)
                if expand_columns:
                    columns = [(cc[0], nc[0] - 1) for cc, nc in zip(columns, columns[1:])] + [
                        columns[-1]
                    ]
            elif columns:  # Fetch cells
                if allow_extend:
                    # Find which spaces between column not empty
                    ll = len(line)
                    for i, (f, t) in enumerate(columns):
                        if t < ll and line[t].strip():
                            # If spaces not empty - shift column width equal size row
                            shift = len(line[f:].split()[0]) - (t - f)
                            # Enlarge column
                            columns[i] = (f, t + shift)
                            # Shift rest
                            columns[i + 1 :] = [
                                (v[0] + shift, v[1] + shift) for v in columns[i + 1 :]
                            ]
                            break
                if allow_wrap:
                    row = [line[f:t] for f, t in columns]
                    if r and not row[0].strip():
                        # first column is empty
                        for i, x in enumerate(row):
                            if (
                                x.strip()
                                and not r[-1][i].endswith(n_row_delim)
                                and not x.startswith(n_row_delim)
                            ):
                                if strip_rows:
                                    r[-1][i] += "%s%s" % (n_row_delim, x.strip())
                                else:
                                    r[-1][i] += "%s%s" % (n_row_delim, x)
                            else:
                                if strip_rows:
                                    r[-1][i] += x.strip()
                                else:
                                    r[-1][i] += x
                    else:
                        r += [row]
                else:
                    r += [[line[f:t].strip() for f, t in columns]]
        if allow_wrap:
            return [[x.strip() for x in rr] for rr in r]
        else:
            return r

    def get_local_iface(self):
        r = {}
        names = {x: y for y, x in six.iteritems(self.scripts.get_ifindexes())}
        # Get LocalPort Table
        for port_num, port_subtype, port_id, port_descr in self.snmp.get_tables(
            [
                mib["LLDP-MIB::lldpLocPortIdSubtype"],
                mib["LLDP-MIB::lldpLocPortId"],
                mib["LLDP-MIB::lldpLocPortDesc"],
            ]
        ):
            if port_subtype == LLDP_PORT_SUBTYPE_ALIAS:
                # Iface alias
                iface_name = port_descr
            elif port_subtype == LLDP_PORT_SUBTYPE_MAC:
                # Iface MAC address
                raise NotImplementedError()
            elif port_subtype == LLDP_PORT_SUBTYPE_LOCAL and port_id.isdigit():
                # Iface local (ifindex)
                iface_name = names[int(port_id)]
            else:
                # Iface local
                iface_name = port_id
            r[port_num] = {"local_interface": iface_name, "local_interface_subtype": port_subtype}
        if not r:
            self.logger.warning(
                "Not getting local LLDP port mappings. Check 1.0.8802.1.1.2.1.3.7 table"
            )
            raise NotImplementedError()
        return r

    def execute_snmp(self):
        neighb = (
            "remote_chassis_id_subtype",
            "remote_chassis_id",
            "remote_port_subtype",
            "remote_port",
            "remote_port_description",
            "remote_system_name",
        )
        r = []
        local_ports = self.get_local_iface()
        if self.has_snmp():
            for v in self.snmp.get_tables(
                [
                    mib["LLDP-MIB::lldpRemLocalPortNum"],
                    mib["LLDP-MIB::lldpRemChassisIdSubtype"],
                    mib["LLDP-MIB::lldpRemChassisId"],
                    mib["LLDP-MIB::lldpRemPortIdSubtype"],
                    mib["LLDP-MIB::lldpRemPortId"],
                    mib["LLDP-MIB::lldpRemPortDesc"],
                    mib["LLDP-MIB::lldpRemSysName"],
                ],
                bulk=True,
            ):
                if v:
                    neigh = dict(zip(neighb, v[2:]))
                    # cleaning
                    if neigh["remote_port_subtype"] == LLDP_PORT_SUBTYPE_COMPONENT:
                        neigh["remote_port_subtype"] = LLDP_PORT_SUBTYPE_ALIAS
                    neigh["remote_port"] = neigh["remote_port"].strip(
                        smart_text(" \x00")
                    )  # \x00 Found on some devices
                    if neigh["remote_chassis_id_subtype"] == LLDP_CHASSIS_SUBTYPE_MAC:
                        neigh["remote_chassis_id"] = MAC(neigh["remote_chassis_id"])
                    if neigh["remote_port_subtype"] == LLDP_PORT_SUBTYPE_MAC:
                        try:
                            neigh["remote_port"] = MAC(neigh["remote_port"])
                        except ValueError:
                            self.logger.warning(
                                "Bad MAC address on Remote Neighbor: %s", neigh["remote_port"]
                            )
                    r += [
                        {
                            "local_interface": local_ports[v[0].split(".")[1]]["local_interface"],
                            # @todo if local interface subtype != 5
                            # "local_interface_id": 5,
                            "neighbors": [neigh],
                        }
                    ]
        return r

    def execute_cli(self):
        r = []
        # Fallback to CLI
        lldp = self.cli("show lldp neighbors")
        for link in self.parse_table(lldp, allow_wrap=True, expand_tabs=False, strip_rows=True):
            local_interface = link[0]
            remote_chassis_id = link[1]
            remote_port = link[2]
            remote_system_name = link[3]
            # Build neighbor data
            # Get capability
            cap = lldp_caps_to_bits(
                link[4].strip().split(","),
                {
                    "O": LLDP_CAP_OTHER,
                    "r": LLDP_CAP_REPEATER,
                    "B": LLDP_CAP_BRIDGE,
                    "W": LLDP_CAP_WLAN_ACCESS_POINT,
                    "R": LLDP_CAP_ROUTER,
                    "T": LLDP_CAP_TELEPHONE,
                    "D": LLDP_CAP_DOCSIS_CABLE_DEVICE,
                    "S": LLDP_CAP_STATION_ONLY,  # S-VLAN
                    "C": 256,  # C-VLAN
                    "H": 512,  # Host
                    "TP": 1024,  # Two Ports MAC Relay
                },
            )
            if is_ipv4(remote_chassis_id) or is_ipv6(remote_chassis_id):
                remote_chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS
            elif is_mac(remote_chassis_id):
                remote_chassis_id = MACAddressParameter().clean(remote_chassis_id)
                remote_chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_MAC
            else:
                remote_chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_LOCAL

            # Get remote port subtype
            remote_port_subtype = LLDP_PORT_SUBTYPE_ALIAS
            if is_ipv4(remote_port):
                # Actually networkAddress(4)
                remote_port_subtype = LLDP_PORT_SUBTYPE_NETWORK_ADDRESS
            elif is_mac(remote_port):
                # Actually macAddress(3)
                # Convert MAC to common form
                remote_port = MACAddressParameter().clean(remote_port)
                remote_port_subtype = LLDP_PORT_SUBTYPE_MAC
            elif is_int(remote_port):
                # Actually local(7)
                remote_port_subtype = LLDP_PORT_SUBTYPE_LOCAL
            i = {"local_interface": local_interface, "neighbors": []}
            n = {
                "remote_chassis_id": remote_chassis_id,
                "remote_chassis_id_subtype": remote_chassis_id_subtype,
                "remote_port": remote_port,
                "remote_port_subtype": remote_port_subtype,
                "remote_capabilities": cap,
            }
            if remote_system_name:
                n["remote_system_name"] = remote_system_name
            #
            # XXX: Dirty hack for older firmware. Switch rebooted.
            #
            if remote_chassis_id_subtype != LLDP_CHASSIS_SUBTYPE_LOCAL:
                i["neighbors"] = [n]
                r += [i]
                continue
            try:
                c = self.cli("show lldp neighbors %s" % local_interface)
                match = self.rx_detail.search(c)
                if match:
                    remote_chassis_id = match.group("dev_id")
                    if is_ipv4(remote_chassis_id) or is_ipv6(remote_chassis_id):
                        remote_chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS
                    elif is_mac(remote_chassis_id):
                        remote_chassis_id = MACAddressParameter().clean(remote_chassis_id)
                        remote_chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_MAC
                    else:
                        remote_chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_LOCAL
                    n["remote_chassis_id"] = remote_chassis_id
                    n["remote_chassis_id_subtype"] = remote_chassis_id_subtype
                    if match.group("sys_name").strip():
                        sys_name = match.group("sys_name").strip()
                        n["remote_system_name"] = sys_name
                    if match.group("sys_descr").strip():
                        sys_descr = match.group("sys_descr").strip()
                        n["remote_system_description"] = sys_descr
                    if match.group("port_descr").strip():
                        port_descr = match.group("port_descr").strip()
                        n["remote_port_description"] = port_descr
            except Exception:
                pass
            i["neighbors"] += [n]
            r += [i]
        return r
