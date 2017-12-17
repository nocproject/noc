# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Huawei
# OS:     VRP
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from collections import defaultdict
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Huawei.VRP"
    pattern_more = [
        (r"^  ---- More ----", " "),
        (r"[Cc]ontinue?\S+", "y\n\r"),
        (r"[Cc]onfirm?\S+", "y\n\r"),
        (r" [Aa]re you sure?\S+", "y\n\r"),
        (r"^Delete flash:", "y\n\r"),
        (r"^Squeeze flash:", "y\n\r")
    ]
    pattern_prompt = \
        r"^[<#\[](?P<hostname>[a-zA-Z0-9-_\\\.\[\(/`'\"\|\s:,=]+)" \
        r"(?:-[a-zA-Z0-9/]+)*[>#\]\)]"
    pattern_syntax_error = \
        r"(ERROR: |% Wrong parameter found at|" \
        r"% Unrecognized command found at|" \
        r"Error:Too many parameters found|" \
        r"% Too many parameters found at|" \
        r"% Ambiguous command found at|" \
        r"Error:\s*Unrecognized command found at|" \
        r"Error:\s*Wrong parameter found at|" \
        r"Error:\s*Incomplete command found at)"

    command_more = " "
    config_volatile = ["^%.*?$"]
    command_disable_pager = "screen-length 0 temporary"
    command_enter_config = "system-view"
    command_leave_config = "return"
    command_save_config = "save"
    command_exit = "quit"
    rogue_chars = [re.compile(r"\x1b\[42D\s+\x1b\[42D"), "\r"]
    default_parser = "noc.cm.parsers.Huawei.VRP.base.BaseVRPParser"

    def generate_prefix_list(self, name, pl, strict=True):
        p = "ip ip-prefix %s permit %%s" % name
        if not strict:
            p += " le 32"
        return "undo ip ip-prefix %s\n" % name + "\n".join(
            [p % x.replace("/", " ") for x in pl])

    rx_interface_name = re.compile(
        r"^(?P<type>XGE|Ten-GigabitEthernet|(?<!100)GE|Eth|MEth)"
        r"(?P<number>[\d/]+(\.\d+)?)$")

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("XGE2/0/0")
        'XGigabitEthernet2/0/0'
        >>> Profile().convert_interface_name("Ten-GigabitEthernet2/0/0")
        'XGigabitEthernet2/0/0'
        >>> Profile().convert_interface_name("GE2/0/0")
        'GigabitEthernet2/0/0'
        >>> Profile().convert_interface_name("Eth2/0/0")
        'Ethernet2/0/0'
        >>> Profile().convert_interface_name("MEth2/0/0")
        'M-Ethernet2/0/0'
        """
        s = str(s)  # avoid `expected string or buffer` error
        match = self.rx_interface_name.match(s)
        if not match:
            return s
        return "%s%s" % ({
            "Loop": "LoopBack",
            "Ten-GigabitEthernet": "XGigabitEthernet",
            "XGE": "XGigabitEthernet",
            "GE": "GigabitEthernet",
            "Eth": "Ethernet",
            "MEth": "M-Ethernet",
            "VE": "Virtual-Ethernet"
            # "Vlanif": "Vlan-interface" - need testing
        }[match.group("type")], match.group("number"))

    def convert_mac(self, mac):
        """
        Convert 00:11:22:33:44:55 style MAC-address to 0011-2233-4455
        """
        v = mac.replace(":", "").lower()
        return "%s-%s-%s" % (v[:4], v[4:8], v[8:])

    spaces_rx = re.compile("^\s{42}|^\s{16}", re.DOTALL | re.MULTILINE)

    def clean_spaces(self, config):
        config = self.spaces_rx.sub("", config)
        return config

    def fix_version(self, v):
        # CLI return S5628F-HI as platform, but SNMP return S5628F
        BAD_PLATFORMS = ["S5628F", "S5628F-HI"]
        if v["platform"] in BAD_PLATFORMS and v["version"] == "5.20":
            # Do not change these numbers. Used in get_switchport script
            v["version"] = "3.10"
        return v["version"]

    @staticmethod
    def parse_table(block, part_name=None):
        """
        :param part_name: If not None - part name not on block
        :type part_name: str
        :param block: Block with table
        :type block: str
        :return:
        """
        k_v_splitter = re.compile(
            r"\s*(?P<key>.+?):\s+(?P<value>.+?)(?:\s\s|\n)", re.IGNORECASE)
        part_splitter = re.compile(
            r"\s*(?P<part_name>\S+?):\s*\n", re.IGNORECASE)
        r = {}
        is_table = False
        is_part = False
        k_v_list = []
        row = []
        if part_name:
            is_part = True
        for l in block.splitlines(True):
            # print l
            # Part section
            if "-" * 5 in l:
                is_table = True
                # print("Table start")
                continue
            if part_splitter.match(l) and is_part:
                # @todo many table in part ?
                is_part = False
                is_table = False
                r[part_name] = dict(k_v_list)
                r[part_name]["table"] = row
                # print("Key-Val: %s" % k_v_list)
                # print("Part End")
                k_v_list = []
                row = []
            if part_splitter.match(l) and not is_part:
                is_part = True
                part_name = part_splitter.match(l).group(1)
                # print("Part start: %s" % part_name)
                continue
            if not l.strip():
                # is_part = False
                # print("Part End")
                continue
            # Parse Section
            if is_part and is_table:
                row.append(l.split())
            elif is_part and not is_table:
                k_v_list.extend(k_v_splitter.findall(l))
            continue
        else:
            r[part_name] = dict(k_v_list)
            if row:
                r[part_name]["table"] = row
            # r[part_name] = dict(k_v_list)
            # r[part_name]["table"] = row
        return r

    @staticmethod
    def parse_ifaces(e=""):
        # Parse display interfaces output command for Huawei
        r = defaultdict(dict)
        current_iface = ""
        for line in e.splitlines():
            print line
            if not line:
                continue
            if (line.startswith("LoopBack") or line.startswith("MEth") or
                    line.startswith("Ethernet") or
                    line.startswith("GigabitEthernet") or line.startswith("XGigabitEthernet") or
                    line.startswith("Vlanif") or line.startswith("NULL")):
                current_iface = line.split()[0]
                continue
            # k, v count
            split = line.count(":") + line.count(" is ") + line.count(" rate ")
            if "Switch Port" in line:
                line = line[12:]
            elif "Route Port" in line:
                line = line[11:]
            print line
            # while split:
            for part in line.split(",", split - 1):
                if ":" in part:
                    k, v = part.split(":", 1)
                elif " is " in part:
                    k, v = part.split("is", 1)
                elif " rate " in part:
                    k, v = part.split("rate", 1)
                    k = k + "rate"
                else:
                    continue
                r[current_iface][k.strip()] = v.strip()
        return r
