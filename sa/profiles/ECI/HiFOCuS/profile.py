# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: ECI http://www.ecitele.com/
# OS:     HiFOCuS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "ECI.HiFOCuS"
    pattern_username = r"^[Ll]ogin :"
    pattern_password = r"^[Pp]assword :"
    username_submit = "\r\n"
    password_submit = "\r\n"
    # command_submit = "\r\n"
    command_submit = "\r\n"
    pattern_prompt = r"^( >>|\S+ >(?: \S+ >)?|\S+ (?:\- SHOW(?:\\\S+)?)?>)"
    pattern_syntax_error = r": no such command"
    pattern_operation_error = r"\S+:\s*Illegal shelf \(\d+\)"

    # pattern_prompt = r"^Select menu option.*:"
    pattern_more = [
        (r"Enter <CR> for more or 'q' to quit--:", "\r"),
        (r"press <SPACE> to continue or <ENTER> to quit", " "),
        (r"(\+-*)+", "\r"),  # Periodically stuck CLI on large table
    ]
    command_exit = "logout"
    # telnet_slow_send_password = True
    # telnet_send_on_connect = "\r"
    # convert_mac = BaseProfile.convert_mac_to_dashed

    def setup_script(self, script):
        if script.parent is None:
            user = script.credentials.get("user", "")
            # Add three random chars to begin of `user`
            # Do not remove this
            script.credentials["user"] = "   " + user

    INTERFACE_TYPES = {
        "lo": "loopback",  # Loopback
        "fe": "physical",  # FortyGigabitEthernet
        "vn": "physical",  # FortyGigabitEthernet
        "en": "physical",  # FortyGigabitEthernet
        "at": "physical",  # FortyGigabitEthernet
        "cp": "physical",  # FortyGigabitEthernet
        "sw": "SVI",
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get((name[:2]).lower())

    rx_snmp_iface = re.compile(
        r".+:\s*Shelf-(?P<shelf>\d+)\s*Interface-(?P<slot>\d+)\s*"
        r"Port-(?P<port>\d+)\s*Mani-(?P<mani>\d+)\s*"
        r"Layer-(?P<layer>\d+)\s*Loc-(?P<loc>\d+)\s*Uni-(?P<uni>\d+)\s*"
    )

    def convert_interface_name(self, s):
        match = self.rx_snmp_iface.match(s)
        # if s.startswith("ATM If"):
        if match:
            # SNMP format
            if int(match.group("uni")) == 0:
                return "%(shelf)s/%(slot)s/%(port)s/%(mani)s" % match.groupdict()
            return "%(shelf)s/%(slot)s/%(port)s/%(mani)s.%(layer)s:%(uni)s" % match.groupdict()
        return s

    rx_header = re.compile(r"(?:\=+\|?)+")

    rx_column_split = re.compile(r"\s*\|\s*")

    def parse_table(self, v):
        v = self.rx_header.split(v)
        for line in v[-1].splitlines():
            line = line.strip()
            if not line:
                continue
            yield self.rx_column_split.split(line)

    def get_boards(self, script, shelf_num=0):
        """
        Parse board table and return active
        :param script:
        :param shelf_num:
        :return: List boards
        :rtype: dict
        """
        v = script.cli("GETPOP %d" % shelf_num, cached=True)
        r = []
        for row in self.parse_table(v):
            slot, card_type, ports, _, _, _, _ = row
            if "EMPTY" in card_type:
                continue
            r += [
                {
                    "slot": int(slot.strip()),
                    "card_type": card_type.strip(),
                    "ports": int(ports.strip()),
                }
            ]
        return r
