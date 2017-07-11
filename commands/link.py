# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Link management CLI interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import argparse
from collections import defaultdict
# NOC modules
from noc.core.management.base import BaseCommand, CommandError
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link


class Command(BaseCommand):
    help = "Show Links"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        # show command
        show_parser = subparsers.add_parser("show",
                                            help="Show link")
        show_parser.add_argument("-m", "--show-method",
                                 dest="show_method",
                                 action="store_true",
                                 help="Show discovery method")
        show_parser.add_argument("args",
                                 nargs=argparse.REMAINDER,
                                 help="Show discovery method")
        # add command
        add_parser = subparsers.add_parser("add",
                                           help="Add link")
        add_parser.add_argument("args",
                                nargs=argparse.REMAINDER,
                                help="Show discovery method")
        # remove command
        remove_parser = subparsers.add_parser("remove",
                                              help="Remove link")
        remove_parser.add_argument("args",
                                   nargs=argparse.REMAINDER,
                                   help="Show discovery method")

    def handle(self, *args, **options):
        print args
        action = options["cmd"]
        if not action:
            action = "show"
        getattr(self, "handle_%s" % action)(*args, **options)

    def show_link(self, link, show_method=False):
        def format_interface(i):
            return "%s@%s" % (i.managed_object.name, i.name)

        i = defaultdict(list)
        for li in link.interfaces:
            i[li.managed_object] += [li]
        r = []
        for mo in i:
            r += [", ".join(format_interface(li) for li in i[mo])]
        l = " --- ".join(r)
        if show_method:
            l += " [%s]" % link.discovery_method
        self.stdout.write(l)

    def handle_show(self, *args, **options):
        show_method = options.get("show_method")
        if args:
            # Show single link
            for i in args:
                iface = Interface.get_interface(i)
                if iface:
                    l = Link.objects.filter(interfaces=iface.id).first()
                    if l:
                        self.show_link(l, show_method)
        else:
            # Show all links
            for l in Link.objects.all():
                self.show_link(l, show_method)

    def handle_add(self, *args, **options):
        """
        Add link
        :param args:
        :param options:
        :return:
        """
        if len(args) != 2:
            raise CommandError(
                "Usage: ./noc link --add <iface1> <iface2>")
        i1 = Interface.get_interface(args[0])
        if not i1:
            raise CommandError("Invalid interface: %s" % args[0])
        i2 = Interface.get_interface(args[1])
        if not i2:
            raise CommandError("Invalid interface: %s" % args[1])
        try:
            i1.link_ptp(i2)
        except ValueError, why:
            raise CommandError(str(why))

    def handle_remove(self, *args, **options):
        """
        Remove link
        :param args:
        :param options:
        :return:
        """
        for i in args:
            iface = Interface.get_interface(i)
            if iface:
                iface.unlink()

if __name__ == "__main__":
    Command().run()
