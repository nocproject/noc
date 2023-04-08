# ---------------------------------------------------------------------
# Interface profile management
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import argparse
from functools import partial

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.main.models.label import Label
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.resourcegroup import ResourceGroup
from noc.core.text import alnum_key


class Command(BaseCommand):
    help = "Apply interface classification"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        # extract command
        show_parser = subparsers.add_parser("show", help="Show interface profiles")
        show_parser.add_argument("mos", nargs=argparse.REMAINDER, help="List of object to showing")
        # clean command
        reset_parser = subparsers.add_parser("reset", help="Reset interface profile")
        reset_parser.add_argument("mos", nargs=argparse.REMAINDER, help="List of object to showing")
        # load command
        apply_parser = subparsers.add_parser("apply", help="Apply classification rules")
        apply_parser.add_argument(
            "--reset-default",
            action="store_true",
            default=False,
            help="Set not matched profile to default",
        )
        apply_parser.add_argument("mos", nargs=argparse.REMAINDER, help="List of object to showing")

    def handle(self, cmd, *args, **options):
        connect()
        if "mos" in options:
            moo = options["mos"]
        else:
            self.stdout.write("No ManagedObject for proccessed")
            self.die("No ManagedObject for proccessed")
            return False
        return getattr(self, "handle_%s" % cmd.replace("-", "_"))(moo, *args, **options)

    @staticmethod
    def get_objects(exprs):
        objects = set()
        for s in exprs:
            objects.update(
                ResourceGroup.get_objects_from_expression(s, model_id="sa.ManagedObject")
            )
        return sorted(objects, key=lambda x: x.name)

    @staticmethod
    def get_interfaces(mo):
        return sorted(
            Interface.objects.filter(managed_object=mo.id, type__in=["physical", "aggregated"]),
            key=lambda x: alnum_key(x.name),
        )

    @staticmethod
    def get_interface_template(interfaces):
        il = max(len(i.name) for i in interfaces)
        il = max(il, 15)
        tps = "    %%-%ds  %%-12s  %%-30s  %%s ;%%s\n" % il
        return tps

    def show_interface(self, tpl, i, status, effective_labels=None):
        if i.description:
            d = i.description[:30]
        else:
            d = ""
        el = ",".join(effective_labels or [])
        self.stdout.write(tpl % (i.name, i.status, d, status, el))

    def handle_show(self, moo, *args, **options):
        for o in self.get_objects(moo):
            self.stdout.write(
                "%s (%s):\n" % (o.name, (o.platform.name if o.platform else None) or o.profile.name)
            )
            ifaces = self.get_interfaces(o)
            if not ifaces:
                self.stdout.write("No interfaces on object\n")
                continue
            tps = self.get_interface_template(ifaces)
            for i in ifaces:
                self.show_interface(tps, i, i.profile.name if i.profile else "-", [])

    def handle_reset(self, moo, *args, **kwargs):
        for o in self.get_objects(moo):
            self.stdout.write(
                "%s (%s):\n" % (o.name, (o.platform.name if o.platform else None) or o.profile.name)
            )
            for i in Interface.objects.filter(managed_object=o.id):
                if i.profile:
                    self.stdout.write("    resetting profile on %s to default\n" % i.name)
                    i.profile = InterfaceProfile.get_default_profile()
                    i.save()

    def handle_apply(self, moo, *args, **kwargs):
        default_profile = InterfaceProfile.get_default_profile()
        for o in self.get_objects(moo):
            self.stdout.write(f"{o.name} ({getattr(o, 'platform', '')}), {o.effective_labels}:\n")
            ifaces = self.get_interfaces(o)
            if not ifaces:
                self.stdout.write("No ifaces on object\n")
                continue
            i_cache = {i.id: i for i in ifaces}
            tps = self.get_interface_template(ifaces)
            pcache = {}
            members = {}
            for i_id, i_name, pn in Label.iter_document_profile(
                "inv.Interface",
                "inv.InterfaceProfile",
                query_filter=[("managed_object", o.id), ("type", ["physical", "aggregated"])],
            ):
                i = i_cache.get(i_id)
                # pn = InterfaceProfile.get_by_id(p_id)
                if i.aggregated_interface:
                    members[i] = pn
                if pn and pn == i.profile.id:
                    v = f"Already Set: {i.profile.name}"
                elif pn:
                    p = pcache.get(pn)
                    if not p:
                        p = InterfaceProfile.get_by_id(pn)
                        pcache[pn] = p
                    i.profile = p
                    i.save()
                    v = f"Set {p.name}"
                else:
                    v = "Not matched"
                    if kwargs.get("reset_default") and i.profile != default_profile:
                        i.profile = default_profile
                        i.save()
                        v = "Not matched. Reset to default"
                self.show_interface(
                    tps, i, v, None
                )  # set(i.effective_labels) - set(o.effective_labels))

    def handle_apply_direct(self, moo, *args, **kwargs):
        # sol = config.get("interface_discovery", "get_interface_profile")
        # @todo Classification pyrule
        default_profile = InterfaceProfile.get_default_profile()
        get_profile = partial(Label.get_instance_profile, InterfaceProfile)
        pcache = {}
        for o in self.get_objects(moo):
            self.stdout.write(
                "%s (%s):\n" % (o.name, o.platform.name if o.platform else o.profile.name)
            )
            ifaces = self.get_interfaces(o)
            if not ifaces:
                self.stdout.write("No ifaces on object\n")
                continue
            tps = self.get_interface_template(ifaces)
            oel = set(o.effective_labels or [])
            for i in ifaces:
                if not i.profile or not i.profile_locked:
                    el = Label.merge_labels(Interface.iter_effective_labels(i))
                    pn = get_profile(el)
                    if pn and pn == i.profile.id:
                        v = f"Already Set: {i.profile.name}"
                    elif pn:
                        p = pcache.get(pn)
                        if not p:
                            p = InterfaceProfile.get_by_id(pn)
                            pcache[pn] = p
                        i.profile = p
                        i.save()
                        v = f"Set {p.name}"
                    else:
                        v = "Not matched"
                        if kwargs.get("reset_default") and i.profile != default_profile:
                            i.profile = default_profile
                            i.save()
                            v = "Not matched. Reset to default"
                    self.show_interface(tps, i, v, set(el) - oel)


if __name__ == "__main__":
    Command().run()
