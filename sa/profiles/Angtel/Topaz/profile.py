# ---------------------------------------------------------------------
# Vendor: Angtel (Angstrem telecom - http://www.angtel.ru/)
# OS:     Topaz
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Angtel.Topaz"

    pattern_unprivileged_prompt = rb"^(?P<hostname>\S+)\s*>"
    pattern_prompt = rb"^(?P<hostname>\S+)\s*(?:\(config[^\)]*\))?#"
    pattern_syntax_error = rb"% Unrecognized command|% Wrong number of parameters"
    command_super = b"enable"
    command_disable_pager = "terminal datadump"
    # rogue_chars = [re.compile(r"\[\x1b\[1mN\x1b\[0m\]")]
    pattern_more = [
        (rb"More: <space>,  Quit: q or CTRL+Z, One line: <return>", b"a"),
        (rb"^Overwrite file \[\S+\]\.+\s*\(Y/N\).+", b"Y\n"),
        (rb"^\s*This action will cause loss of configuration.Proceed\?\s*\(Y/N\)", b"Y\n"),
    ]
    command_exit = "exit"

    def convert_interface_name(self, interface):
        if str(interface) == "0":
            return "CPU"
        if interface.isdigit():
            # Vlan
            interface = "Vlan %s" % interface
        return self.convert_interface_name_cisco(interface)

    def setup_session(self, script):
        # Do not erase this.
        # Account, obtained through RADIUS required this.
        # v = script.cli("show privilege")
        # if ("15" not in v) and script.credentials["super_password"]:
        #    script.cli("enable\n%s" % script.credentials["super_password"])
        script.cli("show privilege")

    INTERFACE_TYPES = {
        "fa": "physical",  # FastEthernet
        "gi": "physical",  # GigabitEthernet
        "te": "physical",  # TenGigabitEthernet
        "po": "aggregated",  # Port-channel/Portgroup
        "vl": "SVI",  # Vlan
    }

    @classmethod
    def get_interface_type(cls, name):
        if name.isdigit():
            # Vlan
            return "SVI"
        return cls.INTERFACE_TYPES.get(name[:2].lower())
