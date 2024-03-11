# ---------------------------------------------------------------------
# Vendor: TPLink
# OS:     T2600G
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "TPLink.T2600G"

    pattern_username = rb"^User:"
    pattern_more = [(rb"Press any key to continue \(Q to quit\)", b" ")]
    pattern_unprivileged_prompt = rb"^\S+?>"
    pattern_syntax_error = (
        rb".*(?:Error: (Invalid parameter.)|(Bad command)|(Missing parameter data)).*"
    )
    command_super = b"enable"
    pattern_prompt = rb"^(?P<hostname>[a-zA-Z0-9/.]\S{0,35})(?:[-_\d\w]+)?(?:\(config[^\)]*\))?#"
    command_disable_pager = "terminal length 0"
    username_submit = b"\r\n"
    password_submit = b"\r\n"
    command_submit = b"\r\n"
    command_enter_config = "configure"
    command_leave_config = "end"
    command_exit = "exit"
    command_save_config = "copy running-config startup-config\n"
    requires_netmask_conversion = True
    rx_ifname = re.compile(r"^((?P<type>Gi|Te|.*)\d\/\d\/)*(?P<number>\d+).*$")
    matchers = {"is_platform_T2600G": {"platform": {"$regex": r"T2600G.*"}}}

    config_tokenizer = "indent"
    config_normalizer = "TPLinkT2600GNormalizer"

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("gigabitEthernet 1/0/24 : copper")
        'Gi1/0/24'
        >>> Profile().convert_interface_name("24")
        'Gi1/0/24'
        >>> Profile().convert_interface_name("ten-gigabitEthernet 1/0/25")
        'Te1/0/25
        """
        match = self.rx_ifname.match(s)
        if match:
            if "Te" in match.group("type") or "ten" in match.group("type"):
                return "Te1/0/%s" % int(match.group("number"))
            return "Gi1/0/%d" % int(match.group("number"))
        else:
            return s

    INTERFACE_TYPES = {
        "gi": "physical",  # gigabitethernet
        "fa": "physical",  # fastethernet
        "ex": "physical",  # extreme-ethernet
        "te": "physical",
        "vl": "SVI",  # vlan
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get((name[:2]).lower())
