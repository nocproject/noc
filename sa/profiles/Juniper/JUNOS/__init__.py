# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Juniper
# OS:     JUNOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Juniper.JUNOS"
    pattern_username = "^((?!Last)\S+ login|[Ll]ogin):"
    pattern_prompt = \
        r"^(({master(?::\d+)}\n)?\S+>)|(({master(?::\d+)})?" \
        r"\[edit.*?\]\n\S+#)|(\[Type \^D at a new line to end input\])"
    pattern_more = [
        (r"^---\(more.*?\)---", " "),
        (r"\? \[yes,no\] .*?", "y\n")
    ]
    pattern_syntax_error = \
        r"^(\'\S+\' is ambiguous\.|syntax error|unknown command\.)"
    command_disable_pager = "set cli screen-length 0"
    command_enter_config = "configure"
    command_leave_config = "commit and-quit"
    command_exit = "exit"
    default_parser = "noc.cm.parsers.Juniper.JUNOS.base.BaseJUNOSParser"

    matchers = {
        "is_switch": {
            "platform": {
                "$regex": "ex|mx|qfx|acx"
            }
        }
    }

    def cmp_version(self, x, y):
        """
        Compare versions.

        Version format:
        <major>.<minor>R<h>.<l>
        """
        def c(v):
            v = v.upper()
            l, r = v.split("R")
            return [int(x) for x in l.split(".")] + [
                int(x) for x in r.split(".")
            ]

        return cmp(c(x), c(y))

    def generate_prefix_list(self, name, pl):
        """
        prefix-list generator. _pl_ is a list of (prefix, min_len, max_len)
        """
        rf = []
        for prefix, min_len, max_len in pl:
            if min_len == max_len:
                rf += ["    route-filter %s exact;" % prefix]
            else:
                rf += ["    route-filter %s upto /%d" % (prefix, max_len)]
        r = [
            "term pass {",
            "    from {"
        ]
        r += rf
        r += [
            "    }",
            "    then next policy;",
            "}",
            "term reject {",
            "    then reject;",
            "}"
        ]
        return "\n".join(r)

    def get_interface_names(self, name):
        """
        TODO: for QFX convert it from ifIndex
        QFX send like:
        Port type          : Locally assigned
        Port ID            : 546
        """
        names = []
        n = self.convert_interface_name(name)
        if n.endswith(".0"):
            names += [n[:-2]]
        return names

    internal_interfaces = re.compile(
        r"^(lc-|cbp|demux|dsc|gre|ipip|lsi|mtun|pimd|pime|pp|tap|pip|sp-|"
        r"em|jsrv|pfe|pfh|vcp|mt-|pd|pe|vt-|vtep|ms-|pc-|me0|sp-|fab|mams-|"
        r"bme|esi|ams)")
    internal_interfaces_olive = re.compile(
        r"^(lc-|cbp|demux|dsc|gre|ipip|lsi|mtun|pimd|pime|pp|tap|pip|sp-)")

    def valid_interface_name(self, name, platform):
        if platform == "olive":
            internal = self.internal_interfaces_olive
        else:
            internal = self.internal_interfaces
        # Skip internal interfaces
        if internal.search(name):
            return False
        if "." in name:
            try:
                ifname, unit = name.split(".")
            except:
                return True
            # See `logical-interface-unit-range`
            if int(unit) > 16385:
                return False
        return True
