# ---------------------------------------------------------------------
# Qtech.QSW2800 Profile
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from dateutil.parser import parse, ParserError

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Qtech.QSW2800"
    pattern_more = [
        (rb"^\s*--More--\s*$", b" "),
        (rb"^Confirm to overwrite current startup-config configuration [Y/N]:", b"\nY\n"),
        (rb"^Confirm to overwrite current startup-config configuration", b"\ny\n"),
        (rb"^Confirm to overwrite the existed destination file?", b"\ny\n"),
    ]
    pattern_unprivileged_prompt = rb"^\S+>"
    pattern_syntax_error = (
        rb"% (?:Invalid input detected at '\^' marker|"
        rb"(?:Ambiguous|Incomplete|.+Unknown) command)|"
        rb"Error input in the position market by"
        rb"|Unknown command"
    )
    command_disable_pager = "terminal length 0"
    command_super = b"enable"
    command_enter_config = "configure"
    command_leave_config = "end"
    command_save_config = "copy running-config startup-config"
    username_submit = b"\r\n"
    password_submit = b"\r\n"
    command_submit = b"\r"
    pattern_prompt = (
        rb"^(?P<hostname>[a-zA-Z0-9]\S{0,40})(?:\(sdiag\))?(?:[\.\-_\d\w]+)?(?:\(config[^\)]*\))?#"
    )

    config_tokenizer = "indent"
    config_tokenizer_settings = {"line_comment": "!"}
    config_normalizer = "Qtech2800Normalizer"
    confdb_defaults = [
        ("hints", "interfaces", "defaults", "admin-status", True),
        ("hints", "protocols", "lldp", "status", False),
        ("hints", "protocols", "ntp", "mode", "server"),
        ("hints", "protocols", "ntp", "version", "3"),
        # ("hints", "protocols", "loop-detect", "status", False),
    ]

    matchers = {
        "is_new_metric": {"caps": {"$in": ["Qtech | OID | Memory Usage 11"]}},
        "is_support_mac_version": {
            "$or": [{"version": {"$gte": "6.3.100.12"}}, {"version": {"$lte": "6.0"}}]
        },
        "is_stack": {"caps": {"$in": ["Stack | Members"]}},
        "is_stackable": {"platform": {"$regex": r"QSW-8200-28F-AC-DC"}},
        "is_qsw3750": {"platform": {"$regex": r"QSW-(?:3750|2850|4610|3470|3500)"}},
        "is_old_version": {"version": {"$regex": r"8.1.1.(?:398|296|431|458|426|406)"}},
    }

    rx_date_format = re.compile(r"(\S+)\s*\((.+)\)")
    rx_path_version = re.compile(r"(\S+)\s*\((\S+)\)")

    @classmethod
    def cmp_version(cls, v1, v2):
        """
        Compare two versions.
        Default implementation compares a versions in format
        N1. .. .NM
        On Qtech.QSW2800
        """
        if not cls.rx_path_version.match(v1) and cls.rx_date_format.match(v1):
            v_part, d_part = cls.rx_date_format.match(v1).groups()
            try:
                d_part = parse(d_part)
                v1 = f"{v_part} {d_part.isoformat()}"
            except ParserError:
                pass
        if not cls.rx_path_version.match(v2) and cls.rx_date_format.match(v2):
            v_part, d_part = cls.rx_date_format.match(v2).groups()
            try:
                d_part = parse(d_part)
                v2 = f"{v_part} {d_part.isoformat()}"
            except ParserError:
                pass
        return super().cmp_version(v1, v2)

    rx_ifname = re.compile(r"^(?P<number>\d+)$")
    rx_split_ifname = re.compile(r"^(Eth|Et)\s*(\d+(?:\/\d+)*)$")

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("Ethernet1/1")
        'Ethernet1/1'
        >>> Profile().convert_interface_name("Eth5/0/19")
        'Ethernet5/0/19'
        >>> Profile().convert_interface_name("1")
        'Ethernet1/1'
        """
        match = self.rx_ifname.match(s)
        if match:
            return "Ethernet1/%d" % int(match.group("number"))
        elif self.rx_split_ifname.match(s):
            return "Ethernet%s" % self.rx_split_ifname.match(s).group(1)
        else:
            return s

    _IF_TYPES = {
        "eth": "physical",
        "vla": "SVI",
        "vsf": "aggregated",
        "po ": "aggregated",
        "por": "aggregated",
        "l2o": "tunnel",
        "loo": "loopback",
        "vpl": "other",
    }

    @classmethod
    def get_interface_type(cls, name):
        if name == "Ethernet0":
            return "management"
        return cls._IF_TYPES.get(name[:3].lower(), "unknown")

    @staticmethod
    def parse_table(block, part_name=None):
        """
        :param part_name: If not None - part name not on block
        :type part_name: str
        :param block: Block with table
        :type block: str
        :return:
        """
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
    def convert_sfp(sfp_type, distance, bit_rate, wavelength):
        if " m" in distance:
            # convert to km
            distance = str(int(distance.split(" ")[0]) / 1000)
        if " nm" in wavelength:
            wavelength = wavelength.split(" ")[0]
        if sfp_type and sfp_type != "unknown":
            return ""
        elif sfp_type == "unknown":
            return "-".join(["QSC", "SFP" + distance + "GE", wavelength])
        else:
            return ""
