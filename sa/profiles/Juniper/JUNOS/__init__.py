# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Juniper
# OS:     JUNOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
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
        r"\'\S+\' is ambiguous\.|syntax error, expecting|unknown command\."
    pattern_operation_error = r"error: abnormal communication termination with"
    command_disable_pager = "set cli screen-length 0"
    command_enter_config = "configure"
    command_leave_config = "commit and-quit"
    command_exit = "exit"
    default_parser = "noc.cm.parsers.Juniper.JUNOS.base.BaseJUNOSParser"

    matchers = {
        "is_has_lldp": {
            "platform": {
                "$regex": "ex|mx|qfx|acx"
            }
        },
        "is_switch": {
            "platform": {
                "$regex": "ex|qfx"
            }
        },
        "is_olive": {
            "platform": {
                "$regex": "olive"
            }
        }
    }

    rx_ver = re.compile(r"\d+")

    # https://www.juniper.net/documentation/en_US/junos/topics/reference/general/junos-release-numbers.html
    def cmp_version(self, x, y):
        """
        Compare versions.

        Version format:
        <major>.<minor>R<h>.<l>
        """
        # FRS/maintenance release software
        if "R" in x and "R" in y:
            pass
        # Feature velocity release software
        elif "F" in x and "F" in y:
            pass
        # Beta release software
        elif "B" in x and "B" in y:
            pass
        # Internal release software:
        # private software release for verifying fixes
        elif "I" in x and "I" in y:
            pass
        # Service release software:
        # released to customers to solve a specific problem—this release
        # will be maintained along with the life span of the underlying release
        elif "S" in x and "S" in y:
            pass
        # Special (eXception) release software:
        # releases that follow a numbering system that differs from
        # the standard Junos OS release numbering
        elif "X" in x and "X" in y:
            pass
        # https://kb.juniper.net/InfoCenter/index?page=content&id=KB30092
        else:
            return None

        a = [int(z) for z in self.rx_ver.findall(x)]
        b = [int(z) for z in self.rx_ver.findall(y)]
        return (a > b) - (a < b)

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
        r"em|jsrv|pfe|pfh|vcp|mt-|pd|pe|vt-|vtep|ms-|pc-|sp-|fab|mams-|"
        r"bme|esi|ams)")
    internal_interfaces_olive = re.compile(
        r"^(lc-|cbp|demux|dsc|gre|ipip|lsi|mtun|pimd|pime|pp|tap|pip|sp-)")

    def valid_interface_name(self, script, name):
        if script.is_olive:
            internal = self.internal_interfaces_olive
        else:
            internal = self.internal_interfaces
        # Skip internal interfaces
        if internal.search(name):
            return False
        if "." in name:
            try:
                ifname, unit = name.split(".")
            except ValueError:
                return True
            # See `logical-interface-unit-range`
            if int(unit) > 16385:
                return False
        return True

    def command_exist(self, script, cmd):
        c = script.cli(
            "help apropos \"%s\" | match \"^show %s\" " % (cmd, cmd),
            cached=True, ignore_errors=True
        )
        return ("show " + cmd in c) and ("error: nothing matches" not in c)
