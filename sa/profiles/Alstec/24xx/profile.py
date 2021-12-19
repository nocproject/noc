# ---------------------------------------------------------------------
# Vendor: Alstec
# OS:     24xx
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile
from noc.core.confdb.syntax.patterns import ANY


class Profile(BaseProfile):
    name = "Alstec.24xx"
    pattern_username = rb"^User:"
    pattern_unprivileged_prompt = rb"^(?P<hostname>[ \S]+) >"
    pattern_prompt = rb"^(?=[^#])(?P<hostname>\S+?)(\s\([\S ]+?\)){0,3} #"
    # (?=[^#]) fix if use banner '# Banner message #' format
    pattern_more = [
        (rb"^--More-- or \(q\)uit$", b" "),
        (
            rb"This operation may take a few minutes.\n"
            rb"Management interfaces will not be available during this time.\n"
            rb"Are you sure you want to save\?\s*\(y/n\):\s*",
            b"y\n",
        ),
        (rb"Would you like to save them now\?", b"n"),
    ]
    pattern_syntax_error = rb"(ERROR: Wrong or incomplete command|Incomplete command\. Use \? to list commands|\^\n% Invalid input detected at '\^' marker)"
    command_super = b"enable"
    command_exit = "logout"
    command_enter_config = "configure"
    command_leave_config = "exit"
    command_save_config = "write memory"
    config_volatile = [r"^!System Up Time.+?\n!Current SNTP Synchronized Time.+?\n"]
    config_tokenizer = "context"
    config_tokenizer_settings = {
        "line_comment": "!",
        "contexts": [
            ["vlan", "database"],
            ["policy-map", ANY, ANY],
            ["policy-map", ANY, ANY, "class", ANY],
            ["interface"],
        ],
        "end_of_context": "exit",
    }

    matchers = {"is_builtin_controller": {"platform": {"$in": ["ALS24110P", "ALS-24110P"]}}}

    rx_physical_port = re.compile(r"^d\+\/\d+")

    @classmethod
    def get_interface_type(cls, name):
        if name.startswith("CPU"):
            return "SVI"
        if cls.rx_physical_port.match(name):
            return "physical"
        return "other"

    rx_ip_interface = re.compile(r"\s*CPU\s+Interface\s*:\s*(\d+\/\d+)")

    def convert_interface_name(self, s):
        if self.rx_ip_interface.match(s):
            return self.rx_ip_interface.match(s).group(1)
        return s

    @staticmethod
    def parse_kv_out(out):
        r = {}
        for line in out.splitlines():
            if "....." in line:
                el1, el2 = line.split(".....", 1)
                r[el1.strip(".").strip()] = el2.strip(".").strip()
        return r

    rx_bad_platform = re.compile(r"^(ALS)(\d+(?:LVT|P))$")

    def normalize_platform(self, name):
        """
        Some equal devices but different platform name:
         ALS-24100LVT, ALS24100LVT, ALS24110LVT, ALS-24110LVT
        :param name:
        :type name: str
        :return:
        :rtype: str

        >>> Profile().normalize_platform("ALS24100LVT")
        'ALS-24100LVT'
        >>> Profile().normalize_platform("ALS-24100LVT")
        'ALS-24100LVT'
        >>> Profile().normalize_platform("ALS24110LVT")
        'ALS-24110LVT'
        """
        if self.rx_bad_platform.match(name):
            name = "%s-%s" % self.rx_bad_platform.match(name).groups()
        return name
