# ----------------------------------------------------------------------
# ./noc segment command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse

# NOC modules
from noc.core.management.base import BaseCommand
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.networksegmentprofile import NetworkSegmentProfile
from noc.core.mongo.connection import connect
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.biosegtrial import BioSegTrial
from noc.inv.models.link import Link
from noc.core.bioseg.moderator.base import moderate_trial
from noc.core.datastream.change import bulk_datastream_changes


class Command(BaseCommand):
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        #
        split_floating_parser = subparsers.add_parser("split-floating")
        split_floating_parser.add_argument("--profile", help="Floating segment profile id")
        split_floating_parser.add_argument("ids", nargs=argparse.REMAINDER, help="Segment ids")
        #
        reactivate_floating_parser = subparsers.add_parser("reactivate-floating")
        reactivate_floating_parser.add_argument("ids", nargs=argparse.REMAINDER, help="Segment ids")
        #
        subparsers.add_parser("show-trials")
        #
        moderate_trials_parser = subparsers.add_parser("moderate-trials")
        moderate_trials_parser.add_argument("ids", nargs=argparse.REMAINDER, help="Trial ids")
        #
        retry_trials_parser = subparsers.add_parser("retry-trials")
        retry_trials_parser.add_argument("ids", nargs=argparse.REMAINDER, help="Trial ids")
        #
        subparsers.add_parser("show-floating")

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd.replace("-", "_"))(*args, **options)

    def handle_split_floating(self, profile, ids, *args, **options):
        connect()
        p = NetworkSegmentProfile.objects.filter(name=profile).first()
        if not p:
            self.die("Profile not found")
        if p.is_persistent:
            self.die("Segment profile cannot be persistent")
        for seg_id in ids:
            seg = NetworkSegment.get_by_id(seg_id)
            if not seg:
                self.print("@@@ %s - not found. Skipping" % seg_id)
                continue
            self.print("@@@ Splitting %s (%s)" % (seg.name, seg_id))
            objects = list(ManagedObject.objects.filter(is_managed=True, segment=seg_id))
            for mo in objects:
                new_segment = NetworkSegment(name="Bubble for %s" % mo.name, profile=p)
                new_segment.save()
                self.print("  Moving '%s' to segment '%s'" % (mo.name, new_segment.name))
                mo.segment = new_segment
                mo.save()
            # Establish trials
            print("@@@ Scheduling trials")
            for mo in objects:
                for link in Link.object_links(mo):
                    for ro in link.managed_objects:
                        if ro == mo:
                            continue
                        print(
                            "  '%s' challenging '%s' over %s -- %s"
                            % (mo.segment.name, ro.segment.name, mo.name, ro.name)
                        )
                        BioSegTrial.schedule_trial(mo.segment, ro.segment, mo, ro, reason="link")

    def handle_show_trials(self):
        def q_seg(id):
            ns = NetworkSegment.get_by_id(id)
            if ns:
                return ns.name
            return str(id)

        def q_mo(id):
            mo = ManagedObject.get_by_id(id)
            if mo:
                return mo.name
            return str(id)

        connect()
        self.print(
            "ID | Status | Attacker | Target | Attacker Object | Target Object | Outcome | Error"
        )
        for trial in BioSegTrial.objects.all().order_by("ts"):
            self.print(
                " | ".join(
                    [
                        str(trial.id),
                        "Processed" if trial.processed else "Pending",
                        q_seg(trial.attacker_id),
                        q_seg(trial.target_id),
                        q_mo(trial.attacker_object_id),
                        q_mo(trial.target_object_id),
                        trial.outcome or "-",
                        trial.error or "-",
                    ]
                )
            )

    def handle_moderate_trials(self, ids, *args, **options):
        connect()
        if ids and ids[0] == "next":
            if len(ids) > 1:
                n = int(ids[1])
            else:
                n = 1
            trials = list(BioSegTrial.objects.filter(processed=False).order_by("id")[:n])
        elif ids:
            trials = list(BioSegTrial.objects.filter(processed=False, id__in=ids).order_by("id"))
        else:
            trials = list(BioSegTrial.objects.filter(processed=False).order_by("id"))
        with bulk_datastream_changes():
            for trial in trials:
                self.print("@@@ Processing trial %s" % trial.id)
                moderate_trial(trial)

    def handle_retry_trials(self, ids, *args, **options):
        connect()
        for id in ids:
            trial = BioSegTrial.objects.filter(id=id).first()
            trial.retry()

    def handle_show_floating(self, *args, **options):
        connect()
        non_persistent = [p.id for p in NetworkSegmentProfile.objects.filter(is_persistent=False)]
        n_seg = 0
        n_mo = 0
        for seg in NetworkSegment.objects.filter(profile__in=non_persistent).order_by("id"):
            objects = list(ManagedObject.objects.filter(segment=seg).order_by("name"))
            power = sum(mo.object_profile.level for mo in objects)
            self.print(
                "@@@ %s (%d objects, power = %d, id = %s)" % (seg.name, len(objects), power, seg.id)
            )
            for mo in objects:
                self.print("    %s" % mo.name)
                n_mo += 1
            n_seg += 1
        self.print("### %d objects are floating in %d segments" % (n_mo, n_seg))

    def handle_reactivate_floating(self, ids, *args, **options):
        connect()
        for seg_id in ids:
            seg = NetworkSegment.get_by_id(seg_id)
            if not seg:
                self.print("@@@ %s - not found. Skipping" % seg_id)
                continue
            self.print("@@@ Reactivating %s (%s)" % (seg.name, seg_id))
            objects = list(ManagedObject.objects.filter(is_managed=True, segment=seg_id))
            # Establish trials
            for mo in objects:
                for link in Link.object_links(mo):
                    for ro in link.managed_objects:
                        if ro == mo:
                            continue
                        print(
                            "  '%s' challenging '%s' over %s -- %s"
                            % (mo.segment.name, ro.segment.name, mo.name, ro.name)
                        )
                        BioSegTrial.schedule_trial(mo.segment, ro.segment, mo, ro, reason="link")


if __name__ == "__main__":
    Command().run()
