# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------
# Vendor: Qtech
# OS:     QSW2800
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""

# Python modules
import re
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Qtech.QSW2800"
    pattern_more = [
        (r"^ --More-- $", " "),
        (r"^Confirm to overwrite current startup-config configuration "
            r"[Y/N]:", "\nY\n"),
        (r"^Confirm to overwrite current startup-config configuration",
            "\ny\n"),
        (r"^Confirm to overwrite the existed destination file?", "\ny\n"),
    ]
    pattern_unpriveleged_prompt = r"^\S+>"
    pattern_syntax_error = r"% (?:Invalid input detected at '\^' marker|" \
                           r"(?:Ambiguous|Incomplete|.+Unknown) command)|" \
                           r"Error input in the position market by"
    command_disable_pager = "terminal length 0"
    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "end"
    command_save_config = "copy running-config startup-config"
    command_submit = "\r"
    pattern_prompt = \
        r"^(?P<hostname>[a-zA-Z0-9]\S{0,19})(?:[\.\-_\d\w]+)?" \
        r"(?:\(config[^\)]*\))?#"

    rx_ifname = re.compile(r"^(?P<number>\d+)$")
    default_parser = "noc.cm.parsers.Qtech.QSW2800.base.BaseQSW2800Parser"

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("Ethernet1/1")
        'Ethernet1/1'
        >>> Profile().convert_interface_name("1")
        'Ethernet1/1'
        """
        match = self.rx_ifname.match(s)
        if match:
            return "Ethernet1/%d" % int(match.group("number"))
        else:
            return s

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
    def convert_sfp(sfp_type, distance, bit_rate, wavelength):
        print sfp_type, distance, bit_rate, wavelength
        if " m" in distance:
            # convert to km
            distance = str(int(distance.split(" ")[0])/1000)
        if " nm" in wavelength:
            wavelength = wavelength.split(" ")[0]
        if sfp_type and sfp_type != "unknown":
            return ""
        elif sfp_type == "unknown":
            return "-".join(["QSC", "SFP" + distance + "GE", wavelength])
        else:
            return ""
