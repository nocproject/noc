# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Extreme
# OS:     XOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Extreme.XOS"
    pattern_prompt = r"^(\*\s)?(Slot-\d+ )?\S+? #"
    pattern_syntax_error = \
        r"%% (Incomplete command|Invalid input detected at)"
    command_disable_pager = "disable clipaging"
    pattern_more = [
        (r"^Press <SPACE> to continue or <Q> to quit:", " "),
        (r"^Do you want to continue with download and remove existing files from internal-memory\? \(y/N\)", "y\n"),
        (r"Do you want to install image after downloading\? \(y - yes, n - no, \<cr\> - cancel\)", "y\n"),
        (r"Are you sure you want to reboot the stack\? \(y/N\)", "y\n"),
        (r"Do you want to save configuration changes to currently selected configuration file (primary.cfg) and reboot?"
         r"(y - save and reboot, n - reboot without save, <cr> - cancel command)", "y\n"),
        (r"Do you want to save configuration to \S+ and overwrite it\? \(y/N\)", "y\n")
    ]

    def get_interface_names(self, name):
        """
        TODO: for QFX convert it from ifIndex
        QFX send like:
        Port type          : Locally assigned
        Port ID            : 546
        """
        names = []
        if ":" in name:
            names += [name.split(":")[-1]]
        return names
