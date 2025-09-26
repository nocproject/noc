# ----------------------------------------------------------------------
# ./noc segment command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
import datetime
from typing import Optional, List, Set, Dict, DefaultDict
from collections import defaultdict

# NOC modules
from noc.core.management.base import BaseCommand
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.networksegmentprofile import NetworkSegmentProfile
from noc.core.mongo.connection import connect
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.biosegtrial import BioSegTrial
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from noc.core.bioseg.moderator.base import moderate_trial
from noc.core.change.policy import change_tracker
from noc.core.text import alnum_key
from noc.core.clickhouse.connect import connection
from noc.inv.models.discoveryid import DiscoveryID
from noc.core.mac import MAC


class Command(BaseCommand):
    MAC_WINDOW = 2 * 86400
    GET_MACS_SQL = """
    SELECT argMax(ts, ts), argMax(interface, ts), mac
    FROM mac
    WHERE managed_object = %s
      AND interface IN (%s)
      AND date >= toDate('%s')
      AND ts >= toDateTime('%s')
    GROUP BY mac
    """

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        split_floating_parser = subparsers.add_parser("split-floating")
        split_floating_parser.add_argument("--profile", help="Floating segment profile id")
        split_floating_parser.add_argument("ids", nargs=argparse.REMAINDER, help="Segment ids")
        reactivate_floating_parser = subparsers.add_parser("reactivate-floating")
        reactivate_floating_parser.add_argument("--profile", help="Floating segment profile id")
        reactivate_floating_parser.add_argument(
            "--allow_persistent", action="store_true", help="Allow trial persistent segment"
        )
        reactivate_floating_parser.add_argument("ids", nargs=argparse.REMAINDER, help="Segment ids")
        vacuum_bulling_parser = subparsers.add_parser("vacuum-bulling")
        vacuum_bulling_parser.add_argument(
            "ids", nargs=argparse.REMAINDER, help="Managed Object ids"
        )
        subparsers.add_parser("show-trials")
        moderate_trials_parser = subparsers.add_parser("moderate-trials")
        moderate_trials_parser.add_argument("ids", nargs=argparse.REMAINDER, help="Trial ids")
        retry_trials_parser = subparsers.add_parser("retry-trials")
        retry_trials_parser.add_argument("ids", nargs=argparse.REMAINDER, help="Trial ids")
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
                new_segment = NetworkSegment(
                    name=mo.administrative_domain.get_bioseg_floating_name(mo)
                    or "Bubble for %s" % mo.name,
                    profile=p,
                    parent=mo.administrative_domain.get_bioseg_floating_parent_segment(),
                )
                new_segment.save()
                self.print("  Moving '%s' to segment '%s'" % (mo.name, new_segment.name))
                mo.segment = new_segment
                mo.save()
            # Establish trials
            self.print("@@@ Scheduling trials")
            for mo in objects:
                for link in Link.object_links(mo):
                    for ro in link.managed_objects:
                        if ro == mo:
                            continue
                        self.print(
                            "  '%s' challenging '%s' over %s -- %s"
                            % (mo.segment.name, ro.segment.name, mo.name, ro.name)
                        )
                        BioSegTrial.schedule_trial(mo.segment, ro.segment, mo, ro, reason="link")

    def handle_vacuum_bulling(self, ids, *args, **kwargs):
        connect()
        for mo_id in ids:
            mo = ManagedObject.get_by_id(mo_id)
            if not mo:
                self.print("@@@ %s is not found, skipping", mo_id)
                continue
            self.print("@@@ %s (%s, %s)", mo.name, mo.address, mo.id)
            # Get interfaces suitable for bulling
            bulling_ifaces: Set[Interface] = {
                iface
                for iface in Interface.objects.filter(managed_object=mo.id)
                if not iface.profile.allow_vacuum_bulling
            }
            if not bulling_ifaces:
                self.print("No interfaces suitable for vacuum bulling")
                continue
            # Get MAC addresses for bulling
            t0 = datetime.datetime.now() - datetime.timedelta(seconds=self.MAC_WINDOW)
            t0 = t0.replace(microsecond=0)
            sql = self.GET_MACS_SQL % (
                mo.bi_id,
                ", ".join("'%s'" % iface.name.replace("'", "''") for iface in bulling_ifaces),
                t0.date().isoformat(),
                t0.isoformat(sep=" "),
            )
            ch = connection()
            last_ts: Optional[str] = None
            all_macs: List[str] = []
            mac_iface: Dict[str, str] = {}
            for ts, iface, mac in ch.execute(post=sql):
                if last_ts is None:
                    last_ts = ts
                elif last_ts > ts:
                    continue
                m = str(MAC(int(mac)))
                all_macs += [m]
                mac_iface[m] = iface
            # Resolve MACs to known chassis-id
            mac_map = DiscoveryID.find_objects(all_macs)
            # Filter suitable rivals
            seg_ifaces: DefaultDict[NetworkSegment, Set[str]] = defaultdict(set)
            iface_segs: DefaultDict[str, Set[NetworkSegment]] = defaultdict(set)
            for mac, r_mo in mac_map.items():
                iface = mac_iface.get(mac)
                if not iface:
                    continue
                seg_ifaces[r_mo.segment].add(iface)
                iface_segs[iface].add(r_mo.segment)
            rej_ifaces: Set[str] = set()
            for seg in seg_ifaces:
                if len(seg_ifaces[seg]) > 1 or seg.profile.is_persistent or seg == mo.segment:
                    # Seen on multiple interfaces or persistent segment or same segment
                    rej_ifaces |= set(seg_ifaces[seg])
                    continue
            for iface in sorted(iface_segs, key=alnum_key):
                if iface in rej_ifaces:
                    continue
                for seg in iface_segs[iface]:
                    self.print("  '%s' challenging '%s' on %s" % (mo.segment.name, seg.name, iface))
                    BioSegTrial.schedule_trial(seg, mo.segment)

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
        with change_tracker.bulk_changes():
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

    def handle_reactivate_floating(
        self, ids, profile=None, allow_persistent=False, *args, **options
    ):
        connect()
        nsp = NetworkSegmentProfile.objects.fillter(is_persistent=False)
        if profile:
            nsp.filter(name=profile)
        if ids:
            ns = NetworkSegment.objects.filter(id__in=ids)
        elif nsp.count() > 0:
            ns = NetworkSegment.objects.filter(profile__in=nsp)
        else:
            self.die("Setting segment filter condition")
        if profile:
            p = NetworkSegmentProfile.objects.get(name=profile)
            ns = ns.filter(profile=p)
        for seg_id in ns.scalar("id"):
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
                        self.print(
                            "  '%s' challenging '%s' over %s -- %s"
                            % (mo.segment.name, ro.segment.name, mo.name, ro.name)
                        )
                        BioSegTrial.schedule_trial(
                            mo.segment,
                            ro.segment,
                            mo,
                            ro,
                            reason="link",
                        )


if __name__ == "__main__":
    Command().run()
