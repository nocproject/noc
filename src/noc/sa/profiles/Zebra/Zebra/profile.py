# ---------------------------------------------------------------------
# Vendor: Zebra
# OS:     Zebra
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Zebra.Zebra"

    pattern_more = [(rb"^--More-- ", b" ")]
    pattern_unprivileged_prompt = rb"^\S+?>"
    command_super = b"enable"
    pattern_prompt = rb"^\S+?#"
    command_disable_pager = "terminal length 0"
    requires_netmask_conversion = True

    def generate_prefix_list(self, name, pl):
        """
        Generate prefix list _name_. pl is a list of (prefix, min_len, max_len)
        """
        me = f"ip prefix-list {name} permit %s"
        mne = f"ip prefix-list {name} permit %s le %d"
        r = [f"no ip prefix-list {name}"]
        for prefix, min_len, max_len in pl:
            if min_len == max_len:
                r.append(me % prefix)
            else:
                r.append(mne % (prefix, max_len))
        return "\n".join(r)
