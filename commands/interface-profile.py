# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Interface profile management
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import argparse
# NOC modules
from noc.core.management.base import BaseCommand, CommandError
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.interfaceclassificationrule import InterfaceClassificationRule
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.lib.text import split_alnum
from noc.settings import config
from noc.core.handler import get_handler


class Command(BaseCommand):
    help = "Show Links"
    def_iface_prof = InterfaceProfile.get_by_name("default")

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        # extract command
        show_parser = subparsers.add_parser("show",
                                            help="Show interface profiles")
        show_parser.add_argument(
            "mos",
            nargs=argparse.REMAINDER,
            help="List of object to showing"
        )
        # clean command
        reset_parser = subparsers.add_parser("reset",
                                             help="Reset interface profile")
        reset_parser.add_argument(
            "mos",
            nargs=argparse.REMAINDER,
            help="List of object to showing"
        )
        # load command
        apply_parser = subparsers.add_parser("apply",
                                             help="Apply classification rules")
        apply_parser.add_argument(
            "mos",
            nargs=argparse.REMAINDER,
            help="List of object to showing"
        )

    def handle(self, cmd, *args, **options):
        if "mos" in options:
            moo = options["mos"]
        else:
            self.stdout.write("No ManagedObject for proccessed")
            self.die("No ManagedObject for proccessed")
            return False
        return getattr(self, "handle_%s" % cmd)(moo, *args, **options)

    @staticmethod
    def get_objects(exprs):
        objects = set()
        for s in exprs:
            objects.update(ManagedObjectSelector.resolve_expression(s))
        return sorted(objects, key=lambda x: x.name)

    @staticmethod
    def get_interfaces(mo):
        return sorted(
            Interface.objects.filter(
                managed_object=mo.id,
                type="physical"
            ),
            key=split_alnum
        )

    @staticmethod
    def get_interface_template(interfaces):
        il = max(len(i.name) for i in interfaces)
        il = max(il, 15)
        tps = "    %%-%ds  %%-12s  %%-30s  %%s\n" % il
        return tps

    def show_interface(self, tpl, i, status):
        if i.description:
            d = i.description[:30]
        else:
            d = ""
        self.stdout.write(tpl % (i.name, i.status, d, status))

    def handle_show(self, moo, *args, **options):
        for o in self.get_objects(moo):
            self.stdout.write("%s (%s):\n" % (o.name, (o.platform.name if o.platform else None)
                                            or o.profile.name))
            ifaces = self.get_interfaces(o)
            tps = self.get_interface_template(ifaces)
            for i in ifaces:
                self.show_interface(
                    tps, i, i.profile.name if i.profile else "-")

    def handle_reset(self, moo, *args, **kwargs):
        for o in self.get_objects(moo):
            self.stdout.write("%s (%s):\n" % (o.name, (o.platform.name if o.platform else None)
                                              or o.profile.name))
            for i in Interface.objects.filter(managed_object=o.id):
                if i.profile:
                    self.stdout.write("    resetting profile on %s to default\n" % i.name)
                    i.profile = self.def_iface_prof
                    i.save()

    def handle_apply(self, moo, *args, **kwargs):
        # sol = config.get("interface_discovery", "get_interface_profile")
        # @todo Classification pyrule
        get_profile = None
        if not get_profile:
            get_profile = InterfaceClassificationRule
            get_profile = get_profile.get_classificator()
            # raise CommandError("No classification solution")
        pcache = {}
        for o in self.get_objects(moo):
            self.stdout.write("%s (%s):" % (o.name, o.platform.name if o.platform else o.profile.name))
            ifaces = self.get_interfaces(o)
            tps = self.get_interface_template(ifaces)
            for i in ifaces:
                if not i.profile or not i.profile_locked:
                    pn = get_profile(i)
                    if pn:
                        p = pcache.get(pn)
                        if not p:
                            p = InterfaceProfile.get_by_id(pn)
                            pcache[pn] = p
                        i.profile = p
                        i.save()
                        v = "Set %s" % p.name
                    else:
                        v = "Not matched"
                    self.show_interface(tps, i, v)

if __name__ == "__main__":
    Command().run()