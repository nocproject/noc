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
import numpy as np
from itertools import izip, izip_longest, dropwhile
from collections import defaultdict
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Huawei.VRP"
    pattern_more = [
        (r"^  ---- More ----\s*", " "),
        (r"[Cc]ontinue?\S+", "y\n\r"),
        (r"[Cc]onfirm?\S+", "y\n\r"),
        (r" [Aa]re you sure?\S+", "y\n\r"),
        (r"^Delete flash:", "y\n\r"),
        (r"^Squeeze flash:", "y\n\r"),
        (
            r"^Warning: The initial password poses security risks.\r\n"
            r"^The password needs to be changed. Change now? [Y/N]:", "n\n\r"
        )
    ]
    pattern_prompt = \
        r"^[<#\[](?P<hostname>[a-zA-Z0-9-_\\\.\[\(/`'\"\|\s:,=]+)" \
        r"(?:-[a-zA-Z0-9/\_]+)*[>#\]\)]"
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

    matchers = {
        "is_kernel_3": {
            "version": {
                "$gte": "3.0",
                "$lt": "5.0"
            }
        },
        "is_kernelgte_5": {
            "version": {
                "$gte": "5.0"
            }
        },
        "is_bad_platform": {
            "version": {
                "$in": ["5.20"]
            },
            "platform": {
                "$in": ["S5628F", "S5628F-HI"]
            }
        },
        "is_ne_platform": {
            "platform": {
                "$regex": "^NE"
            }
        },
        "is_ar": {
            "platform": {
                "$regex": "^AR\d+.+"
            }
        }
    }

    rx_ver = re.compile(r"((?:(\d)\.(\d+))\s*)?\(?(?:V(\d+)|)(?:R(\d+)|)(?:C(\d+)|)(?:B(\d+)|)(?:SPC(\d+)|)\)?")
    rx_ver_kern = re.compile(r"\s*(\d)\.(\d+)\s*")
    rx_ver_rel = re.compile(r"\(?(?:V(\d+)|)(?:R(\d+)|)(?:C(\d+)|)(?:B(\d+)|)(?:SPC(\d+)|)\)?")

    def cmp_version(self, x, y):
        """
        Huawei VRP system software version is divided into "core version" (or "kernel") and "release" two.
        We are talking about is the VRP 1.x, 2.x, 3.x, And now VRP 5.x and 8.x versions.
        Huawei release status of the VRP system is based on V, R, C three letters
        (representing three different version number) were identified, the basic format is VxxxRxxxCxx:
        * Vxxx logo products / solutions change program main product platform, called V version number.
        * Rxxx identification for generic versions of all customers posting, known as the R version number.
        * version of C customized version of the fast to meet the development version of R different types
          based on customer's demand, known as the C version number.
        [Note] the above described V version and R version number, independent number, do not influence each other.
               It is between them and no affiliation. For example, the product can occur platform changes,
               and functional properties remain unchanged,
               such as the original VR version is V100R005, the new VR version V200R005.
          In the same R version, C version of XX from 00 to 1 units numbered. If the R version number change,
          the C version number of the XX began to re numbered 01, such as V100R001C01, V100R001C02, V100R002C01
        :param x: [12358].x (VxxxRxxxCxxBxxx)
        :param y: [12358].x (VxxxRxxxCxxBxxx)
        :return: <0 , if v1<v2
                  0 , if v1==v2
                 >0 , if v1>v2
               None , if v1 and v2 cannot be compared

        >>> Profile().cmp_version("5.30 (V100R005C02B236)", "5.30")
        0
        >>> Profile().cmp_version("5.30 (V100R005C02B236)", "5.40")
        -1
        >>> Profile().cmp_version("R006C02", "5.30 (V100R005C02B236)")
        1
        >>> Profile().cmp_version("5.30 (V100R003C00SPC100)", "5.30 (V100R005C02B236)")
        -1
        >>> Profile().cmp_version("5.80 (V100R005C02SPC100)", "5.80 (V100R005C02B236)")
        0
        >>> Profile().cmp_version("5.00 (V100R005C02SPC100)", "3.80 (V100R005C02B236)")
        1
        >>> Profile().cmp_version("3.10 (V100R005C02SPC100)", "3.80 (V100R005C02B236)")
        -1
        >>> Profile().cmp_version("100", "5.30 (V100R005C02B236)")
        """
        a, b = self.rx_ver.search(str(x)).groups()[1:], self.rx_ver.search(str(y)).groups()[1:]
        # if set(self.rx_ver.search(x).groups()) and self.rx_ver.search(y):
        if any(a) and any(b):
            r = list(dropwhile(lambda s: s == 0,
                               [(int(a) > int(b)) - (int(a) < int(b)) for a, b in izip(a, b)   # noqa
                                if a is not None and b is not None]))
            return r[0] if r else 0
        else:
            return None

    INTERFACE_TYPES = {
        "Aux": "tunnel",
        "Cellular": "tunnel",
        "Eth-Trunk": "aggregated",
        "Ip-Trunk": "aggregated",
        "XGigabitEthernet": "physical",
        "Ten-GigabitEthernet": "physical",
        "GigabitEthernet": "physical",
        "FastEthernet": "physical",
        "Ethernet": "physical",
        "Cascade": "physical",
        "Logic-Channel": "tunnel",
        "LoopBack": "loopback",
        "MEth": "management",
        "M-Ethernet": "management",
        "MTunnel": None,
        "Ring-if": "physical",
        "Tunnel": "tunnel",
        "Virtual-Ethernet": None,
        "Virtual-Template": "template",
        "Bridge-Template": "template",
        "Bridge-template": "template",
        "Vlanif": "SVI",
        "Vlan-interface": "SVI",
        "NULL": "null",
        "RprPos": "unknown",
        "Rpr": "unknown",
        "40GE": "physical",
        "100GE": "physical",
        "Serial": None,
        "Pos": None
    }

    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name)

    def generate_prefix_list(self, name, pl, strict=True):
        me = "ip ip-prefix %s permit %%s" % name
        mne = "ip ip-prefix %s permit %%s le %%d" % name
        r = ["undo ip ip-prefix %s" % name]
        for prefix, min_len, max_len in pl:
            if min_len == max_len:
                r += [me % prefix]
            else:
                r += [mne % (prefix, max_len)]
        return "\n".join(r)

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
        # @todo migrate to parse_block
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
        for line in block.splitlines(True):
            # print l
            # Part section
            if "-" * 5 in line:
                is_table = True
                # print("Table start")
                continue
            if part_splitter.match(line) and is_part:
                # @todo many table in part ?
                is_part = False
                is_table = False
                r[part_name] = dict(k_v_list)
                r[part_name]["table"] = row
                # print("Key-Val: %s" % k_v_list)
                # print("Part End")
                k_v_list = []
                row = []
            if part_splitter.match(line) and not is_part:
                is_part = True
                part_name = part_splitter.match(line).group(1)
                # print("Part start: %s" % part_name)
                continue
            if not line.strip():
                # is_part = False
                # print("Part End")
                continue
            # Parse Section
            if is_part and is_table:
                row.append(line.split())
            elif is_part and not is_table:
                k_v_list.extend(k_v_splitter.findall(line))
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

    @staticmethod
    def update_dict(s, d):
        for k in d:
            if k in s:
                s[k] += d[k]
            else:
                s[k] = d[k]

    @staticmethod
    def parse_header(v):
        """
        Parse header structured multiline format:
        Config    Current Agg     Min    Ld Share  Flags Ld Share  Agg Link  Link Up
        Master    Master  Control Active Algorithm       Group     Mbr State Transitions
        :param v:
        :return: Dictionary {start column position: header}
        {10: 'Config Master', 18: 'Current Master', 26: 'Agg Control', 33: 'Min Active',
         43: 'Ld Share Algorithm', 49: 'Flags ', 59: 'Ld Share Group', 63: 'Agg Mbr', 69: 'Link State'}
        """
        head = []
        empty_header = None
        header = {}

        for num, lines in enumerate(izip_longest(*v, fillvalue='-')):
            #
            if empty_header is None:
                empty_header = (' ',) * len(lines)
                head += [lines]
                continue
            if set(head[-1]) == {' '} and lines != empty_header:
                head = np.array(head)
                # Transpone list header string
                header[num] = " ".join(["".join(s).strip() for s in head.transpose().tolist()])
                head = []
            head += [lines]
        else:
            # last column
            head = np.array(head)
            header[num] = " ".join(["".join(s).strip(" -") for s in head.transpose().tolist()])

        return header

    def parse_block(self, block):
        """
        Block1:
        Local:
        LAG ID: 8                   WorkingMode: LACP
        Preempt Delay: Disabled     Hash arithmetic: According to SIP-XOR-DIP
        System Priority: 32768      System ID: 5489-9875-1457
        Least Active-linknumber: 1  Max Active-linknumber: 8
        Operate status: up          Number Of Up Port In Trunk: 2
        --------------------------------------------------------------------------------
        ActorPortName          Status   PortType PortPri PortNo PortKey PortState Weight
        XGigabitEthernet10/0/4 Selected 10GE     32768   95     2113    10111100  1
        XGigabitEthernet10/0/5 Selected 10GE     32768   96     2113    10111100  1

        Block2:
        Partner:
        --------------------------------------------------------------------------------
        ActorPortName          SysPri   SystemID        PortPri PortNo PortKey PortState
        XGigabitEthernet10/0/4 65535    0011-bbbb-ddda  255     1      33      10111100
        XGigabitEthernet10/0/5 65535    0011-bbbb-ddda  255     2      33      10111100

        :param block:
        :return:
        """

        r = defaultdict(dict)
        part_name = ""
        k_v_splitter = re.compile(
            r"\s*(?P<key>.+?):\s+(?P<value>.+?)(?:\s\s|\n)", re.IGNORECASE)
        part_splitter = re.compile(
            r"\s*(?P<part_name>\S+?):\s*\n", re.IGNORECASE)

        # r = {}
        is_table = False  # Table block, start after -----
        is_table_header = False  # table header first line after ----
        k_v_list = []
        ph = {}
        for line in block.splitlines(True):
            # print l
            # Part section
            if "-" * 5 in line:
                # -- - starting table and end key-value lines
                is_table = True
                is_table_header = True
                r[part_name]["table"] = []
                if k_v_list:
                    r[part_name].update(dict(k_v_list))
                    k_v_list = []
                # print("Table start")
                continue
            if is_table_header:
                # Parse table header for detect column border
                # If needed more than one line - needed count
                ph = self.parse_header([line])
                is_table_header = False
                continue
            if part_splitter.match(line):
                # Part spliter (Local:\n, Partner:\n)
                # or (is_table and not line.strip())
                # @todo many table in part ?
                is_table = False
                ph = {}
                part_name = part_splitter.match(line).group(1)
                continue
            if ":" in line and not is_table:
                # Key-value block
                k_v_list.extend(k_v_splitter.findall(line))
            elif ph and is_table:
                # parse table row
                i = 0
                field = {}
                for num in sorted(ph):
                    # Shift column border
                    left = i
                    right = num
                    v = line[left:right].strip()
                    field[ph[num]] = [v] if v else []
                    i = num
                if not field[ph[min(ph)]] and r[part_name]["table"]:
                    self.update_dict(r[part_name]["table"][-1], field)
                else:
                    r[part_name]["table"] += [field]
        return r
