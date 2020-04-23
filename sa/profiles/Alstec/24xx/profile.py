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
    pattern_username = r"^User:"
    pattern_unprivileged_prompt = r"^(?P<hostname>[ \S]+) >"
    pattern_prompt = r"^(?=[^#])(?P<hostname>\S+?)(\s\([\S ]+?\)){0,3} #"
    # (?=[^#]) fix if use banner '# Banner message #' format
    pattern_more = [
        (r"^--More-- or \(q\)uit$", " "),
        (
            r"This operation may take a few minutes.\n"
            r"Management interfaces will not be available during this time.\n"
            r"Are you sure you want to save\?\s*\(y/n\):\s*",
            "y\n",
        ),
        (r"Would you like to save them now\?", "n"),
    ]
    pattern_syntax_error = r"ERROR: Wrong or incomplete command"
    command_super = "enable"
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

    matchers = {"is_builtin_controller": {"platform": {"$in": ["ALS24110P"]}}}

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
