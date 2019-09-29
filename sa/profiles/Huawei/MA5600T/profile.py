# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Huawei
# OS:     MA5600T
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Huawei.MA5600T"
    pattern_username = r"^>[>\s]User name(|\s\([<\s\w]+\)):"
    pattern_password = r"^>[>\s](?:User )?[Pp]assword(|\s\([<\s\w]+\)):"
    pattern_more = [
        (r"---- More \( Press 'Q' to break \) ----", " "),
        (r"\[<frameId/slotId>\]", "\n"),
        (r"\(y/n\) \[n\]", "y\n"),
        (r"\[to\]\:", "\n"),
        (r"\{ \<cr\>\|vpi\<K\> \}\:", "\n"),
        (r"\{ \<cr\>\|ont\<K\> \}\:", "\n"),
        (r"Are you sure to modify system time?", "n\n"),
        (r"Are you sure to log out?", "y\n"),
        (r"\{ <cr>\|configuration<K>\|data<K> \}", "\n"),
        (r"\{ <cr>\|mode<K> \}", "\n"),
        (r"\{ <cr>\|frameid\/slotid\<S\>\<Length \d+\-15\>(?:\|spm\<K\>|) \}\:", "\n"),
        (r"\{ (?:spm\<K\>\|)?\<cr\>\|frameid/slotid\<S\>\<\d+,15\> \}\:", "\n"),
        (r"\{ <cr>\|backplane\<K\>\|frameid\/slotid\<S\>\<Length \d+\-15\> \}", "\n"),
        (r"\{ <cr>(\|\S+\<K\>)+ \}", "\n"),
        (r"\{ groupindex\<K\>\|<cr> \}\:", "\n"),
        (r"\{ <cr>\|vlanattr\<K\>\|vlantype\<E\>\<\S+\> \}\:", "\n"),
        # The ONT automatic loading policy will be deleted
        (r"\s*Are you sure to proceed\(y/n\)\[[yn]\]", "y\n"),
    ]
    pattern_unprivileged_prompt = r"^(?P<hostname>(?!>)\S+?)>"
    pattern_prompt = (
        r"^(?P<hostname>(?!>)\S+?)(?:-\d+)?(?:\(config\S*[^\)]*\))?(\(diagnose\))?(#|%%)"
    )
    pattern_syntax_error = r"(% Unknown command|  Incorrect command:)"
    pattern_operation_error = "Configuration console time out, please retry to log on"
    # Found on MA5616, V800R015C10
    send_on_syntax_error = BaseProfile.send_backspaces
    command_more = " "
    config_volatile = ["^%.*?$"]
    command_disable_pager = "scroll 512"
    command_super = "enable"
    command_enter_config = "configure terminal"
    command_leave_config = "quit"
    command_save_config = "save\ny\n"
    command_exit = "quit\ny\n"
    rogue_chars = ["\xff", "\r"]
    config_tokenizer = "indent"
    config_tokenizer_settings = {"line_comment": "#"}

    matchers = {
        "is_gpon_uplink": {"platform": {"$in": ["MA5626G"]}},
        "is_dslam": {"platform": {"$in": ["MA5600"]}},
    }

    rx_slots = re.compile(r"^\s*\d+", re.MULTILINE)
    rx_ports = re.compile(
        r"^\s*(?P<port>\d+)\s+(?P<type>ADSL|VDSL|GPON|10GE|GE|FE|GE-Optic|GE-Elec|FE-Elec)\s+.+?"
        r"(?P<state>[Oo]nline|[Oo]ffline|Activating|Activated|Registered)",
        re.MULTILINE,
    )
    rx_splitter = re.compile(r"\s*\-+\n")

    @staticmethod
    def get_board_type(name):
        if "EP" in name or "GP" in name or "XGB" in name:
            return "GPON"
        elif "ETH" in name or "X2C" in name or "GIC" in name or "X1C" in name:
            return "Ethernet"
        elif "CU" in name or "IPMB" in name:
            return "Control"
        elif "AD" in name or "CS" in name:
            return "ADSL"
        return None

    def get_board(self, script):
        r = []
        slots = 0
        v = script.cli("display board 0", cached=True)
        _, header, body, _ = self.rx_splitter.split(v)
        for line in body.splitlines():
            try:
                num, board = line.split(None, 1)
            except ValueError:
                num, board = line.strip(), None
            if board:
                name, status = board.split(None, 2)[:2]
                board_type = self.get_board_type(name)
                r += [{"num": int(num), "name": name, "status": status, "type": board_type}]
            slots += 1
        return slots, r

    def get_slots_n(self, script):
        """
        If slots 7 - MA5603, 14 - MA5600
        :param script:
        :return:
        """
        i = -1
        v = script.cli("display board 0", cached=True)
        for match in self.rx_slots.finditer(v):
            i += 1
        return i + 1

    def get_ports_n(self, script, slot_no):
        i = -1
        t = ""
        s = {}
        v = script.cli(("display board 0/%d" % slot_no), cached=True)
        for match in self.rx_ports.finditer(v):
            i += 1
            t = match.group("type")
            s[match.group("port")] = match.group("state").lower() in [
                "online",
                "activated",
                "registered",
            ]
        return {"n": i, "t": t, "s": s}

    def fill_ports(self, script):
        n = self.get_slots_n(script)
        r = []
        i = 0
        while i <= n:
            r += [self.get_ports_n(script, i)]
            i += 1
        return r

    rx_port_name = re.compile(r"(\S+)(\d+\/\d+\/\d+)")

    def convert_interface_name(self, interface):
        if " " in interface:
            return interface.split()[1]
        if "ethernet" in interface:
            return interface[8:]
        if "GPON" in interface:
            return interface.split()[-1]
        if self.rx_port_name.match(interface):
            return self.rx_port_name.findall(interface)[0][1]
        return interface

    INTERFACE_TYPES = {
        "meth": "management",
        "null": "null",
        "loop": "loopback",
        "vlan": "SVI",
        "seri": "physical",
        "adsl": "physical",
        "gpon": "physical",
        "vdsl": "physical",
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:4].lower())

    @staticmethod
    def update_dict(s, d):
        for k in d:
            if k in s:
                s[k] += d[k]
            else:
                s[k] = d[k]

    def parse_table1(self, table, header):
        r = []
        for line in table.splitlines():
            # parse table row
            if len(line) - len(line.lstrip()) - 2:
                line = line[len(line) - len(str.lstrip(line)) - 2 :]
            i = 0
            field = {}
            for num in sorted(header):
                # Shift column border
                left = i
                right = num
                v = line[left:right].strip()
                field[header[num]] = [v] if v else []
                i = num
            if not field[header[min(header)]]:
                self.update_dict(r[-1], field)
            else:
                r += [field]
        return r

    # SmartAX MA5600T&MA5603T Multi-Service Access Module
    # ifIndex MIB Encoding Rules
    type = {
        "other": 1,
        "ATM": 4,
        "ADSL": 6,
        "Eth": 7,
        "IMA": 39,
        "SHDSL": 44,
        "Vlan": 48,
        "IMALink": 51,
        "Trunk": 54,
        "DOCSISup": 59,
        "DOCSISdown": 60,
        "DOCSISport": 61,
        "BITS": 96,
        "TDME1": 97,
        "VDSL": 124,
        "VDSL2": 124,
        "xDSLchan": 123,
        "GPON": 125,
        "EPON": 126,
        # Dummy rule, needed in MA5626
        # IF-MIB::ifName.4261413120 = STRING: GPONNNI
        "XG-PON": 127,
    }

    @classmethod
    def snmp_index(cls, int_type, shelfID, slotID, intNum):
        """
        Huawei MA5600T&MA5603T port -> ifindex converter
        """

        type_id = cls.type[int_type]
        index = type_id << 25
        index += shelfID << 19
        index += slotID << 13
        if int_type in ["Vlan"]:
            index += intNum
        elif int_type in ["xDSLchan", "DOCSISup", "DOCSISdown"]:
            index += intNum << 5
        # https://gpon.kou.li/huawei/olt/snmp
        elif int_type in ["GPON", "XG-PON"]:
            index += intNum << 8
        else:
            index += intNum << 6
        return index

    class diagnose(object):
        """Switch context manager to use with "with" statement"""

        def __init__(self, script):
            self.script = script

        def __enter__(self):
            """Enter diagnose context"""
            self.script.logger.debug("Enter to diagnose mode")
            self.script.cli("diagnose")

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Leave diagnose context"""
            self.script.logger.debug("Quit diagnose mode")
            self.script.cli("quit")
