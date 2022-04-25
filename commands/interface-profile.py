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
from noc.inv.models.interfaceclassificationrule import InterfaceClassificationRule
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
        apply_parser.add_argument(
            "--use-classification-rule",
            action="store_true",
            default=False,
            help="Use InterfaceClassification Rule for works",
        )
        apply_parser.add_argument("mos", nargs=argparse.REMAINDER, help="List of object to showing")
        apply_confdb_parser = subparsers.add_parser(
            "apply-confdb", help="Apply ConfDB classification rules"
        )
        apply_confdb_parser.add_argument(
            "--reset-default",
            action="store_true",
            default=False,
            help="Set not matched profile to default",
        )
        apply_confdb_parser.add_argument(
            "mos", nargs=argparse.REMAINDER, help="List of object to showing"
        )

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
            Interface.objects.filter(managed_object=mo.id, type="physical"),
            key=lambda x: alnum_key(x.name),
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
            self.stdout.write(
                "%s (%s):\n" % (o.name, (o.platform.name if o.platform else None) or o.profile.name)
            )
            ifaces = self.get_interfaces(o)
            if not ifaces:
                self.stdout.write("No ifaces on object\n")
                continue
            tps = self.get_interface_template(ifaces)
            for i in ifaces:
                self.show_interface(tps, i, i.profile.name if i.profile else "-")

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

    def handle_apply_confdb(self, moo, *args, **kwargs):
        default_profile = InterfaceProfile.get_default_profile()
        for o in self.get_objects(moo):
            self.stdout.write(
                "%s (%s):\n" % (o.name, o.platform.name if o.platform else o.profile.name)
            )
            ifmap = {i.name: i for i in self.get_interfaces(o)}
            if not ifmap:
                self.stdout.write("No ifaces on object\n")
                continue
            tps = self.get_interface_template(ifmap.values())
            proccessed = set()
            selectors_skipping = set()  # if selectors has not match
            cdb = o.get_confdb()
            ifprofilemap = {}
            for icr in InterfaceClassificationRule.objects.filter(is_active=True).order_by("order"):
                if icr.selector.id in selectors_skipping:
                    continue
                r = next(cdb.query(icr.selector.get_confdb_query), None)
                if r is None:
                    # Selectors already fail check
                    selectors_skipping.add(icr.selector.id)
                    continue
                self.print("[%s] Check selector" % icr)
                for match in cdb.query(icr.get_confdb_query):
                    if match["ifname"] in proccessed or match["ifname"] not in ifmap:
                        continue
                    self.print("[%s] Match %s" % (icr, match["ifname"]))
                    iface = ifmap[match["ifname"]]
                    proccessed.add(match["ifname"])
                    if iface.profile_locked:
                        continue
                    ifprofilemap[iface.name] = icr.profile
            # Set profile
            for ifname in ifmap:
                i = ifmap[ifname]
                if ifname in ifprofilemap and i.profile.id != ifprofilemap[ifname].id:
                    i.profile = ifprofilemap[ifname]
                    i.save()
                    v = "Set %s" % ifprofilemap[ifname].name
                elif ifname in ifprofilemap and i.profile.id == ifprofilemap[ifname].id:
                    v = "Already set %s" % ifprofilemap[ifname].name
                else:
                    v = "Not matched"
                    if kwargs.get("reset_default") and i.profile != default_profile:
                        i.profile = default_profile
                        i.save()
                        v = "Not matched. Reset to default"
                self.show_interface(tps, i, v)

    def handle_apply(self, moo, *args, **kwargs):
        # sol = config.get("interface_discovery", "get_interface_profile")
        # @todo Classification pyrule
        default_profile = InterfaceProfile.get_default_profile()
        if kwargs.get("use_classification_rule"):
            get_profile = InterfaceClassificationRule
            get_profile = get_profile.get_classificator()
            # raise CommandError("No classification solution")
        else:
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
            for i in ifaces:
                if not i.profile or not i.profile_locked:
                    pn = get_profile(Label.merge_labels(Interface.iter_effective_labels(i)))
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
                        if kwargs.get("reset_default") and i.profile != default_profile:
                            i.profile = default_profile
                            i.save()
                            v = "Not matched. Reset to default"
                    self.show_interface(tps, i, v)


if __name__ == "__main__":
    Command().run()
