# ---------------------------------------------------------------------
# Vendor: Cisco
# OS:     CatOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Cisco.CatOS"

    pattern_unprivileged_prompt = rb"^\S+?>"
    command_super = "enable"
    pattern_prompt = rb"^\S+?\s+\(enable\)\s+"
    convert_mac = BaseProfile.convert_mac_to_dashed
    pattern_more = [(rb"^--More--$", b" "), (rb"^Do you wish to continue y/n [n]?", b"y\n")]
    config_volatile = [
        r"^This command shows non-default configurations only.*?"
        r"^Use 'show config all' to show both default and non-default "
        r"configurations.",
        r"^\.+\s*$",
        r"^(?:(?:begin)|(?:end))\s*$",
    ]
    rogue_chars = [b"\r", b" \x08", b"\x08"]
