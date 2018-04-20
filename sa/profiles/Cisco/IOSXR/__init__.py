# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: Cisco
# OS:     IOS XR
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
## Vendor: Cisco
## OS:     IOS XR
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

# Python modules
import re
# NOC modules
<<<<<<< HEAD
from noc.core.profile.base import BaseProfile
from noc.sa.interfaces.base import InterfaceTypeError


class Profile(BaseProfile):
    name = "Cisco.IOSXR"
    pattern_more = r"^ --More--"
    pattern_unprivileged_prompt = r"^\S+?>"
=======
from noc.sa.profiles import Profile as NOCProfile
from noc.sa.interfaces import InterfaceTypeError


class Profile(NOCProfile):
    name = "Cisco.IOSXR"
    supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
    pattern_more = r"^ --More--"
    pattern_unpriveleged_prompt = r"^\S+?>"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_syntax_error = r"% Invalid input detected at"
    command_disable_pager = "terminal length 0"
    command_super = "enable"
    command_exit = "exit"
    pattern_prompt = r"^(?P<hostname>\S+?)(?:-\d+)?(?:\(config[^\)]*\))?#"
    requires_netmask_conversion = True
<<<<<<< HEAD
    convert_mac = BaseProfile.convert_mac_to_cisco
=======
    convert_mac = NOCProfile.convert_mac_to_cisco
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    default_parser = "noc.cm.parsers.Cisco.IOSXR.base.BaseIOSXRParser"

    rx_interface_name = re.compile(
        r"^(?P<type>[a-z\-]+)\s*(?P<number>\d+(?:/\d+)*(?:\.\d+)?(?:(?:/RS?P\d+)?/CPU\d+(?:/\d+)*)?)$",
        re.IGNORECASE)

    def convert_interface_name(self, s):
        """
        MgmtEth0/1/CPU0/0
        GigabitEthernet0/2/0/0.1000
        Te0/0/1/3
        """
        match = self.rx_interface_name.match(s)
        if not match:
            raise InterfaceTypeError("Invalid interface '%s'" % s)
        t = match.group(1)[:2]
<<<<<<< HEAD
        if t.lower() == "bu":
=======
        if t.lower() == "Bu":
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            t = "BE"
        return "%s%s" % (t, match.group(2))

    def generate_prefix_list(self, name, pl):
        """
        Generate prefix list _name_. pl is a list of (prefix, min_len, max_len)
        """
        me = " %s"
        mne = " %s le %d"
        r = []
        for prefix, min_len, max_len in pl:
            if min_len == max_len:
                r += [me % prefix]
            else:
                r += [mne % (prefix, max_len)]
        return "\n".join([
            "prefix-set %s" % name,
            ",\n".join(r),
            "end-set"
        ])
