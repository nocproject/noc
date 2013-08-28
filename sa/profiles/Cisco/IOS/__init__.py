# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Cisco
## OS:     IOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.profiles import Profile as NOCProfile


class Profile(NOCProfile):
    name = "Cisco.IOS"
    supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
    pattern_more = [
        (r"^ --More--", "\n"),
        (r"\?\s*\[confirm\]", "\n")
    ]
    pattern_unpriveleged_prompt = r"^\S+?>"
    pattern_syntax_error = r"% Invalid input detected at|% Ambiguous command:|% Incomplete command."
    command_disable_pager = "terminal length 0"
    command_super = "enable"
    command_enter_config = "configure terminal"
    command_leave_config = "end"
    command_exit = "exit"
    command_save_config = "copy running-config startup-config\n"
    pattern_prompt = r"^(?P<hostname>[a-zA-Z0-9]\S{,20}?)(?:-\d+)?(?:\(config[^\)]*\))?#"
    requires_netmask_conversion = True
    convert_mac = NOCProfile.convert_mac_to_cisco
    config_volatile = ["^ntp clock-period .*?^"]

    rx_cable_if = re.compile(r"Cable\s*(?P<pr_if>\d+/\d+) U(pstream)?\s*(?P<sub_if>\d+)", re.IGNORECASE)

    def convert_interface_name(self, interface):
        if interface.lower().startswith("dot11radio"):
            return "Dot11Radio" + interface[10:]
        if interface.lower().startswith("bvi"):
            return "BVI" + interface[3:]
        if interface.lower().startswith("e1"):
            return "E1 %s" % interface[2:].strip()
        if interface.lower().startswith("t1"):
            return "T1 %s" % interface[2:].strip()
        if interface.lower().startswith("fxo null"):
            return "FXO %s" % interface[8:].strip()
        if interface.lower().startswith("fxs"):
            return "FXS %s" % interface[3:].strip()
        if interface.lower().startswith("efxs"):
            return "EFXS %s" % interface[4:].strip()
        if interface.lower().startswith("cpp"):
            return "CPP"
        if interface.lower().startswith("srp"):
            return "SRP %s" % interface[3:].strip()
        match = self.rx_cable_if.search(interface)
        if match:
            return "Ca %s/%s" % match.group('pr_if'), match.group('sub_if')
        return self.convert_interface_name_cisco(interface)

    def generate_prefix_list(self, name, pl):
        """
        Generate prefix list _name_. pl is a list of (prefix, min_len, max_len)
        """
        me = "ip prefix-list %s permit %%s" % name
        mne = "ip prefix-list %s permit %%s le %%d" % name
        r = ["no ip prefix-list %s" % name]
        for prefix, min_len, max_len in pl:
            if min_len == max_len:
                r += [me % prefix]
            else:
                r += [mne % (prefix, max_len)]
        return "\n".join(r)

    def setup_session(self, script):
        """
        Perform session initialization
        Process specific path parameters:
        cluster:id - switch to cluster member
        """
        cluster_member = None
        # Parse path parameters
        for p in script.access_profile.path.split("/"):
            if p.startswith("cluster:"):
                cluster_member = p[8:].strip()
        # Switch to cluster member, if necessary
        if cluster_member:
            script.debug("Switching to cluster member '%s'" % cluster_member)
            script.cli("rc %s" % cluster_member)


def uBR(v):
    """
    uBR series selector
    """
    return "BC" in v["version"]


def MESeries(v):
    """
    MExxxx series selector
    :param v:
    :type v: dict
    :return:
    :rtype: bool
    """
    return v["platform"].startswith("ME")
