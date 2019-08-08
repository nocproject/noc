# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ./noc confdb
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import argparse

# NOC modules
from noc.core.management.base import BaseCommand
from noc.config import config


class Command(BaseCommand):
    PREFIX = config.path.cp_new

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        # syntax command
        syntax_parser = subparsers.add_parser("syntax")
        syntax_parser.add_argument("path", nargs=argparse.REMAINDER)

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_syntax(self, path=None, *args, **kwargs):
        def dump_node(node, level=0, recursive=True):
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
            if recursive and node.children:
                for nc in node.children:
                    dump_node(nc, level + 1)

        def find_root(children, rest_path, level=0):
            if not rest_path:
                return children
            if len(children) == 1 and not children[0].token:
                dump_node(children[0], level, recursive=False)
                return find_root(children[0].children, rest_path[1:], level=level + 1)
            p = rest_path[0]
            for cc in children:
                if cc.token == p:
                    dump_node(cc, level, recursive=False)
                    return find_root(cc.children, rest_path[1:], level=level + 1)

        from noc.core.confdb.syntax.base import SYNTAX

        root = find_root(SYNTAX, path)
        if not root:
            return
        for c in root:
            dump_node(c, level=len(path) if path else 0)


if __name__ == "__main__":
    Command().run()
