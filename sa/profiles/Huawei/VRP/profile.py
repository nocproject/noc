# ---------------------------------------------------------------------
# Huawei,VRP profile
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from itertools import dropwhile
from collections import defaultdict
from itertools import zip_longest

# Third-party modules
import numpy as np

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Huawei.VRP"
    pattern_more = [
        (rb"^  ---- More ----\s*", b" "),
        (rb"[Cc]ontinue?\S+", b"y\n\r"),
        (rb"[Cc]onfirm?\S+", b"y\n\r"),
        (rb"\s*[Aa]re you sure?\S+", b"y\n\r"),
        (rb"^Delete flash:", b"y\n\r"),
        (rb"^Squeeze flash:", b"y\n\r"),
        (rb"^The password needs to be changed\. Change now\? \[Y\/N\]\:", b"n\n\r"),
        (rb"unchanged press the enter key\)\:", b"\n"),
    ]
    pattern_prompt = (
        rb"^[<#\[](~|\*|)(?P<hostname>[a-zA-Z0-9-_\\\.\[\(/`'\"\|\s:,=\+]+)"
        rb"(?:-[a-zA-Z0-9/\_]+)*[>#\]\)]"
    )
    pattern_syntax_error = (
        rb"(ERROR: |% Wrong parameter found at|"
        rb"% Unrecognized command found at|"
        rb"Error:Too many parameters found|"
        rb"% Too many parameters found at|"
        rb"% Ambiguous command found at|"
        rb"Error:\s*Unrecognized command found at|"
        rb"Error:\s*Wrong parameter found at|"
        rb"Error:\s*Incomplete command found at)|"
        rb"Error:\s*Instance can not be used when stp in vbst mode"
    )

    config_volatile = [r"^%.*?$"]
    command_disable_pager = "screen-length 0 temporary"
    command_enter_config = "system-view"
    command_leave_config = "return"
    command_save_config = "save"
    command_exit = "quit"
    rogue_chars = [
        re.compile(rb"\x1b\[42D\s+\x1b\[42D"),
        b"\r",
        re.compile(rb"\x1b\[16D\s+\x1b\[16D"),
    ]
    config_tokenizer = "indent"
    config_tokenizer_settings = {
        # "end_of_context": "#"
    }
    config_normalizer = "VRPNormalizer"
    confdb_defaults = [
        ("hints", "interfaces", "defaults", "admin-status", True),
        ("hints", "protocols", "lldp", "status", True),
        ("hints", "protocols", "spanning-tree", "status", True),
        ("hints", "protocols", "loop-detect", "status", False),
        ("hints", "protocols", "ntp", "mode", "server"),
        ("hints", "protocols", "ntp", "version", "3"),
    ]
    config_applicators = ["noc.core.confdb.applicator.collapsetagged.CollapseTaggedApplicator"]

    port_splitter = ""

    matchers = {
        "is_kernel_3": {"version": {"$gte": "3.0", "$lt": "5.0"}},
        "is_kernelgte_5": {"version": {"$gte": "5.0"}},
        "is_kernelgte_3": {"version": {"$regex": r"^3\..+"}},
        "is_kernelgte_5_3": {"version": {"$regex": r"^5\.3.+"}},
        "is_bad_platform": {
            "version": {"$regex": r"5.20.+"},
            "platform": {"$in": ["S5628F", "S5628F-HI"]},
        },
        "is_ne_platform": {"platform": {"$regex": r"^NE"}},
        "is_ar": {"platform": {"$regex": r"^AR\d+.+"}},
        "is_extended_entity_mib_supported": {"caps": {"$in": ["Huawei | MIB | ENTITY-EXTENT-MIB"]}},
        "is_stack": {"caps": {"$in": ["Stack | Members"]}},
        "is_stack_memory_all": {
            "caps": {"$in": ["Stack | Members", "Huawei | OID | hwMemoryDevTable"]}
        },
        "is_s85xx": {"platform": {"$regex": r"^(S85.+)$"}},
        "is_ar12_93xx": {"platform": {"$regex": r"^(S93..|AR[12].+)$"}},
        "is_cloud_engine": {"platform": {"$regex": r"^CE\S+"}},
        "is_cloud_engine_switch": {"platform": {"$regex": r"^S(6[37]30-H|5[37]3[1256]-[HLS])\S+"}},
        "is_cx600": {"platform": {"$regex": r"^CX600\S*"}},
        "is_cx300": {"platform": {"$regex": r"^CX300\S*"}},
        "is_cx200X": {"platform": {"$regex": r"^CX200\S*"}},
        "is_quidway_S5xxx": {"platform": {"$regex": r"^S5...\S+"}},
        "is_quidway_S9xxx": {"platform": {"$regex": r"^S9...\S*"}},
        "is_s77xx": {"platform": {"$regex": r"^S77\S+"}},
        "is_s127xx": {"platform": {"$regex": r"^S127\S+"}},
    }

    rx_ver = re.compile(
        r"((?:(\d)\.(\d+))\s*)?\(?(?:V(\d+)|)(?:R(\d+)|)(?:C(\d+)|)(?:B(\d+)|)(?:SPC(\d+)|)\)?"
    )
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
            r = list(
                dropwhile(
                    lambda s: s == 0,
                    [
                        (int(a) > int(b)) - (int(a) < int(b))
                        for a, b in zip(a, b)  # noqa
                        if a is not None and b is not None
                    ],
                )
            )
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
        "InLoopBack": "loopback",
        "Console": "SVI",
        "MEth": "management",
        "M-Ethernet": "management",
        "MTunnel": None,
        "Ring-if": "physical",
        "Tunnel": "tunnel",
        "Virtual-Ethernet": "SVI",
        "Virtual-Template": "template",
        "Bridge-Template": "template",
        "Bridge-template": "template",
        "Bridge-if": "SVI",
        "Vlanif": "SVI",
        "Vlan-interface": "SVI",
        "NULL": "null",
        "RprPos": "unknown",
        "Rpr": "unknown",
        "10GE": "physical",
        "25GE": "physical",
        "40GE": "physical",
        "100GE": "physical",
        "Serial": None,
        "Pos": None,
        "Vbdif": "other",
    }

    rx_iftype = re.compile(r"^(\D+?|\d{2,3}\S+?)\d+.*$")

    @classmethod
    def get_interface_type(cls, name):
        if cls.rx_iftype.match(name):
            return cls.INTERFACE_TYPES.get(cls.rx_iftype.match(name).group(1))
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
        r"^(?P<type>XGE|Ten-GigabitEthernet|(?<!100)GE|Gi|G|Eth|MEth)(?P<number>[\d/]+(\.\d+)?)$"
    )

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("XGE2/0/0")
        'XGigabitEthernet2/0/0'
        >>> Profile().convert_interface_name("Ten-GigabitEthernet2/0/0")
        'XGigabitEthernet2/0/0'
        >>> Profile().convert_interface_name("GE2/0/0")
        'GigabitEthernet2/0/0'
        >>> Profile().convert_interface_name("G2/0/0")
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
        return "%s%s" % (
            {
                "Loop": "LoopBack",
                "Ten-GigabitEthernet": "XGigabitEthernet",
                "XGE": "XGigabitEthernet",
                "GE": "GigabitEthernet",  # Sometimes it used on iface description
                "G": "GigabitEthernet",  # Sometimes it used on iface description
                "Gi": "GigabitEthernet",
                "Eth": "Ethernet",
                "MEth": "M-Ethernet",
                "VE": "Virtual-Ethernet",
                # "Vlanif": "Vlan-interface" - need testing
            }[match.group("type")],
            match.group("number"),
        )

    def convert_mac(self, mac):
        """
        Convert 00:11:22:33:44:55 style MAC-address to 0011-2233-4455
        """
        v = mac.replace(":", "").lower()
        return "%s-%s-%s" % (v[:4], v[4:8], v[8:])

    spaces_rx = re.compile(r"^\s{42}|^\s{16}", re.DOTALL | re.MULTILINE)

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
        k_v_splitter = re.compile(r"\s*(?P<key>.+?):\s+(?P<value>.+?)(?:\s\s|\n)", re.IGNORECASE)
        part_splitter = re.compile(r"\s*(?P<part_name>\S+?):\s*\n", re.IGNORECASE)
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
        r[part_name] = dict(k_v_list)
        if row:
            r[part_name]["table"] = row
        return r

    @staticmethod
    def parse_ifaces(e=""):
        # Parse display interfaces output command for Huawei
        r = defaultdict(dict)
        current_iface = ""
        for line in e.splitlines():
            if not line:
                continue
            if (
                line.startswith("LoopBack")
                or line.startswith("MEth")
                or line.startswith("Ethernet")
                or line.startswith("GigabitEthernet")
                or line.startswith("XGigabitEthernet")
                or line.startswith("Vlanif")
                or line.startswith("NULL")
            ):
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

        for num, lines in enumerate(zip_longest(*v, fillvalue="-")):
            #
            if empty_header is None:
                empty_header = (" ",) * len(lines)
                head += [lines]
                continue
            if set(head[-1]) == {" "} and lines != empty_header:
                head = np.array(head)
                # Transpone list header string
                header[num] = " ".join(["".join(s).strip() for s in head.transpose().tolist()])
                head = []
            head += [lines]
        # last column
        head = np.array(head)
        header[num] = " ".join(["".join(s).strip(" -") for s in head.transpose().tolist()])
        return header
