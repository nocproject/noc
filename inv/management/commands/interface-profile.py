# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface profile management
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from optparse import OptionParser, make_option
from collections import defaultdict
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.lib.text import split_alnum
from noc.settings import config
from noc.lib.solutions import get_solution


class Command(BaseCommand):
    help = "Show Links"
    option_list = BaseCommand.option_list + (
        make_option("-s", "--show", dest="action",
            action="store_const", const="show",
            help="Show interface profiles"),
        make_option("-r", "--reset", dest="action",
            action="store_const", const="reset",
            help="Reset interface profile"),
        make_option("-a", "--apply", dest="action",
            action="store_const", const="apply",
            help="Apply classification rules"),
    )

    def handle(self, *args, **options):
        action = options["action"]
        if not action:
            action = "show"
        getattr(self, "handle_%s" % action)(*args, **options)

    def get_objects(self, exprs):
        objects = set()
        for s in exprs:
            objects.update(ManagedObjectSelector.resolve_expression(s))
        return sorted(objects, key=lambda x: x.name)

    def get_interfaces(self, object):
        return sorted(
            Interface.objects.filter(
                managed_object=object.id,
                type="physical"
            ),
            key=split_alnum
        )

    def get_interface_template(self, interfaces):
        il = max(len(i.name) for i in interfaces)
        il = max(il, 15)
        tps = "    %%-%ds  %%-12s  %%-30s  %%s" % il
        return tps

    def show_interface(self, tpl, i, status):
        if i.description:
            d = i.description[:30]
        else:
            d = ""
        print tpl % (i.name, i.status, d, status)

    def handle_show(self, *args, **kwargs):
        for o in self.get_objects(args):
            print "%s (%s):" % (o.name, o.platform or o.profile_name)
            ifaces = self.get_interfaces(o)
            tps = self.get_interface_template(ifaces)
            for i in ifaces:
                self.show_interface(
                    tps, i, i.profile.name if i.profile else "-")

    def handle_reset(self, *args, **kwargs):
        for o in self.get_objects(args):
            print "%s (%s):" % (o.name, o.platform or o.profile_name)
            for i in Interface.objects.filter(managed_object=o.id):
                if i.profile:
                    print "    resetting profile on %s" % i.name
                    i.profile = None
                    i.save()

    def handle_apply(self, *args, **kwargs):
        sol = config.get("interface_discovery", "get_interface_profile")
        get_profile = None
        if sol:
            get_profile = get_solution(sol)
        if not get_profile:
            raise CommandError("No classification solution")
        pcache = {}
        for o in self.get_objects(args):
            print "%s (%s):" % (o.name, o.platform or o.profile_name)
            ifaces = self.get_interfaces(o)
            tps = self.get_interface_template(ifaces)
            for i in ifaces:
                if not i.profile or not i.profile_locked:
                    pn = get_profile(i)
                    if pn:
                        p = pcache.get(pn)
                        if not pn:
                            p = InterfaceProfile.objects.get(name=p)
                            pcache[pn] = p
                        i.profile = p
                        i.save()
                        v = "Set %s" % pn
                    else:
                        v = "Not matched"
                    self.show_interface(tps, i, v)
