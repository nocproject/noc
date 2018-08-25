# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ./noc stencil
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import sys
from collections import defaultdict
# Third-party modules
from jinja2 import Template
# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.stencil import stencil_registry


class Command(BaseCommand):
    INDEX_TEMPLATE_PATH = "templates/stencil_index.html.j2"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        #
        html_parser = subparsers.add_parser("htmlindex")
        html_parser.add_argument(
            "-o", "--out",
            help="Output file"
        )

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_htmlindex(self, out=None, *args, **options):
        stencils = defaultdict(list)
        for stencil_id in sorted(stencil_registry.stencils):
            coll, name = stencil_id.split("/", 1)
            stencils[coll] += [stencil_registry.get(stencil_id)]
        with open(self.INDEX_TEMPLATE_PATH) as f:
            tpl = Template(f.read())
        r = tpl.render({
            "stencils": stencils
        })
        if out:
            with open(out, "w") as f:
                f.write(r)
        else:
            sys.stdout.write(r)


if __name__ == "__main__":
    Command().run()
