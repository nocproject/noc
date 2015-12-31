# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Juniper
## OS:     JUNOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Juniper.JUNOS"
    pattern_username = "^((?!Last)\S+ login|[Ll]ogin):"
    pattern_prompt = r"^(({master(?::\d+)}\n)?\S+>)|(({master(?::\d+)})?\[edit.*?\]\n\S+#)|(\[Type \^D at a new line to end input\])"
    pattern_more = [
        (r"^---\(more.*?\)---", " "),
        (r"\? \[yes,no\] .*?", "y\n")
    ]
    command_disable_pager = "set cli screen-length 0"
    command_enter_config = "configure"
    command_leave_config = "commit and-quit"
    default_parser = "noc.cm.parsers.Juniper.JUNOS.base.BaseJUNOSParser"

    def cmp_version(self, x, y):
        """
        Compare versions.

        Version format:
        <major>.<minor>R<h>.<l>
        """
        def c(v):
            v = v.upper()
            l, r = v.split("R")
            return [int(x) for x in l.split(".")] + [int(x) for x in r.split(".")]

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
            "    from {",
            ]
        r += rf
        r += [
            "    }",
            "    then next policy;",
            "}",
            "term reject {",
            "    then reject;"
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
