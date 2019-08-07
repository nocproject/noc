# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ./noc confdb
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function

# NOC modules
from noc.core.management.base import BaseCommand
from noc.config import config


class Command(BaseCommand):
    PREFIX = config.path.cp_new

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        # syntax command
        subparsers.add_parser("syntax")

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_syntax(self, *args, **kwargs):
        def dump_node(node, level=0):
            indent = "  " * level
            if node.name:
                label = "<%s>" % node.name
            elif node.token is None:
                label = "ANY"
            else:
                label = node.token
            if node.multi:
                label = "*%s" % label
            self.print("%s%s" % (indent, label))
            if node.children:
                for nc in node.children:
                    dump_node(nc, level + 1)

        from noc.core.confdb.syntax.base import SYNTAX

        for c in SYNTAX:
            dump_node(c)


if __name__ == "__main__":
    Command().run()
