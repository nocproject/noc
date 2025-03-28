# ---------------------------------------------------------------------
# Workflow maintenance
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import argparse
import datetime

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.models import get_model
from noc.wf.models.wfmigration import WFMigration


class Command(BaseCommand):
    help = "Workflow maintenance"

    PROFILE_MAP = {
        "crm.SubscriberProfile": "crm.Subscriber",
        "crm.SupplierProfile": "crm.Supplier",
        "ip.AddressProfile": "ip.Address",
        "ip.PrefixProfile": "ip.Prefix",
        "phone.PhoneNumberProfile": "phone.PhoneNumber",
        "phone.PhoneRangeProfile": "phone.PhoneRange",
        "vc.L2DomainProfile": "vc.L2Domain",
        "vc.VLANProfile": "vc.VLAN",
        "vc.VPNProfile": ["vc.VPN", "ip.VRF"],
        "inv.SensorProfile": "inv.Sensor",
        "pm.AgentProfile": "pm.Agent",
        "sa.ServiceProfile": "sa.Service",
        "sa.ManagedObjectProfile": "sa.ManagedObject",
        "sla.SLAProfile": "sla.SLAProbe",
        "peer.PeerProfile": "peer.Peer",
    }

    EXPIRE_MODELS = ["vc.VLAN", "ip.Address"]

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        # extract command
        migrate_parser = subparsers.add_parser("migrate")
        migrate_parser.add_argument(
            "--dry-run",
            dest="dry_run",
            action="store_true",
            help="Dump statistics. Do not perform updates",
        )
        migrate_parser.add_argument("--migration", required=True, help="Migration name")
        migrate_parser.add_argument("--profile", required=True, help="Profile model")
        migrate_parser.add_argument("profiles", help="Profile ids", nargs=argparse.REMAINDER)
        # expire command
        expire_parser = subparsers.add_parser("expire")
        expire_parser.add_argument(
            "--dry-run",
            dest="dry_run",
            action="store_true",
            help="Dump statistics. Do not perform updates",
        )
        expire_parser.add_argument("--model", action="append", help="Models to expire")

    def handle(self, cmd, *args, **options):
        connect()

        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_migrate(
        self, dry_run=False, migration=None, profile=None, profiles=None, *args, **kwargs
    ):
        if profile not in self.PROFILE_MAP:
            self.die(
                "Invalid profile %s. Possible profiles:\n%s"
                % (profile, "\n".join(self.PROFILE_MAP))
            )
        wfm = WFMigration.objects.filter(name=migration).first()
        if not wfm:
            self.die("Invalid migration %s" % wfm.name)
        pmodel = get_model(profile)
        models = self.PROFILE_MAP[profile]
        if isinstance(models, str):
            models = [models]
        imodels = [get_model(model) for model in models]
        for pid in profiles:
            p = pmodel.get_by_id(pid)
            if not p:
                self.die("Profile %s is not found" % pid)
            self.print("Migrating profile %s" % p)
            tr = wfm.get_translation_map(p.workflow)
            if not tr:
                self.print("No translations")
                continue
            for ostate in tr:
                for imodel in imodels:
                    if hasattr(imodel, "object_profile"):
                        kw = {"state": ostate.id, "object_profile": pid}
                    else:
                        kw = {"state": ostate.id, "profile": pid}
                    c = imodel.objects.filter(**kw).count()
                    self.print(
                        f"  {ostate} -> {tr[ostate]}: {c} records in  model '{imodel.__name__}'"
                    )
                    if c and not dry_run:
                        for o in imodel.objects.filter(**kw):
                            o.set_state(tr[ostate])

    def handle_expire(self, dry_run=False, model=None, *args, **kwargs):
        model = model or self.EXPIRE_MODELS
        now = datetime.datetime.now()
        for m in model:
            c = get_model(m)
            if not c:
                self.die("Invalid model: %s" % m)
            if not getattr(c, "_has_expired", False):
                self.die("Model %s does not support expiration" % m)
            self.print("Expiring %s:" % m)
            for c in c.objects.filter(expired__lt=now):
                if not c.state.ttl:
                    continue
                self.print("  %s" % c)
                if not dry_run:
                    c.fire_event("expired")


if __name__ == "__main__":
    Command().run()
