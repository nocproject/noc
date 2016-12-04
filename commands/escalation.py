# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## escalation command
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import argparse
import operator
import cachetools
## Third-party modules
import yaml
## NOC modules
from noc.core.management.base import BaseCommand
from noc.fm.models.alarmescalation import AlarmEscalation
from noc.sa.models.selectorcache import SelectorCache
from noc.fm.models.utils import get_alarm
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.sa.models.serviceprofile import ServiceProfile
from noc.crm.models.subscriberprofile import SubscriberProfile
from noc.inv.models.extnrittmap import ExtNRITTMap
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.ttsystem import TTSystem


class Command(BaseCommand):
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        #
        check_parser = subparsers.add_parser("check")
        check_parser.add_argument(
            "check_alarms",
            nargs=argparse.REMAINDER,
            help="Checks alarms escalation"
        )
        #
        apply_parser = subparsers.add_parser("run")
        apply_parser.add_argument(
            "run_alarms",
            nargs=argparse.REMAINDER,
            help="Run alarm escalations"
        )

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_check(self, check_alarms=None, *args, **kwargs):
        check_alarms = check_alarms or []
        for a_id in check_alarms:
            alarm = get_alarm(a_id)
            if alarm:
                self.check_alarm(alarm)
            else:
                self.stdout.write(
                    "ERROR: Alarm %s is not found. Skipping\n" % alarm
                )

    def handle_run(self, run_alarms=None, *args, **kwargs):
        run_alarms = run_alarms or []
        for a_id in run_alarms:
            alarm = get_alarm(a_id)
            if alarm and alarm.status == "A":
                self.run_alarm(alarm)
            elif alarm:
                self.stdout.write(
                    "ERROR: Alarm %s is cleared. Skipping\n" % alarm
                )
            else:
                self.stdout.write(
                    "ERROR: Alarm %s is not found. Skipping\n" % alarm
                )

    def check_alarm(self, alarm):
        def summary_to_list(summary, model):
            r = []
            for k in summary:
                p = model.get_by_id(k.profile)
                if not p or getattr(p, "show_in_summary", True) == False:
                    continue
                r += [{
                    "profile": p.name,
                    "summary": k.summary
                }]
            return sorted(r, key=lambda x: -x["summary"])

        def iter_consequences(alarm):
            """
            Generator yielding all consequences alarm
            """
            for ac in [ArchivedAlarm, ActiveAlarm]:
                for a in ac.objects.filter(root=alarm.id):
                    yield a
                    for ca in a.iter_consequences():
                        yield ca

        def iter_affected(alarm):
            """
            Generator yielding all affected managed objects
            """
            seen = set([alarm.managed_object])
            yield alarm.managed_object
            for a in iter_consequences(alarm):
                if a.managed_object not in seen:
                    seen.add(a.managed_object)
                    yield a.managed_object

        def iter_escalated(alarm):
            """
            Generator yielding all escalated consequences
            """
            for a in iter_consequences(alarm):
                if a.escalation_tt:
                    yield a

        mo = alarm.managed_object
        self.stdout.write("-" * 72 + "\n")
        self.stdout.write("Alarm Id : %s  Time: %s\n" % (
            alarm.id, alarm.timestamp
        ))
        self.stdout.write("Class    : %s\n" % alarm.alarm_class.name)
        self.stdout.write("Object   : %s  Platform: %s  IP: %s\n" % (
            mo.name, mo.platform, mo.address
        ))
        c = mo.administrative_domain
        adm_domains = [c]
        while c.parent:
            c = c.parent
            adm_domains.insert(0, c)
        self.stdout.write(
            "Adm. Dom.: %s (%s)\n" % (
                " | ".join(c.name for c in adm_domains),
                " | ".join(str(c.id) for c in adm_domains)
            )
        )
        escalations = list(AlarmEscalation.objects.filter(
            alarm_classes__alarm_class=alarm.alarm_class.id
        ))
        if not escalations:
            self.stdout.write("@ No matched escalations\n")
            return
        for esc in escalations:
            self.stdout.write("[Chain: %s]\n" % esc.name)
            if alarm.root:
                self.stdout.write("    @ Not a root cause (Root Id: %s)\n" % alarm.root)
                continue
            for e in esc.escalations:
                self.stdout.write("    [After %ss]\n" % e.delay)
            # Check administrative domain
            if (e.administrative_domain and
                    e.administrative_domain.id not in alarm.adm_path):
                self.stdout.write("    @ Administrative domain mismatch (%s not in %s)\n" % (
                    e.administrative_domain.id, alarm.adm_path
                ))
                continue
            # Check severity
            if e.min_severity and alarm.severity < e.min_severity:
                self.stdout.write("    @ Severity mismatch: %s < %s\n" % (
                    alarm.severity, e.min_severity))
                continue
            # Check selector
            if e.selector and not SelectorCache.is_in_selector(mo, e.selector):
                self.stdout.write("    @ Selector mismatch (%s required)\n" % (
                    e.selector.name))
                continue
            # Check time pattern
            if e.time_pattern and not e.time_pattern.match(alarm.timestamp):
                self.stdout.write("    @ Time pattern mismatch (%s required)\n" % (
                    e.time_pattern.name))
                continue
            # Render escalation message
            if not e.template:
                self.stdout.write("    @ No escalation template\n")
                continue
            # Check whether consequences has escalations
            cons_escalated = sorted(iter_escalated(alarm),
                                    key=operator.attrgetter("timestamp"))
            affected_objects = sorted(iter_affected(alarm),
                                      key=operator.attrgetter("name"))
            #
            ctx = {
                "alarm": alarm,
                "affected_objects": affected_objects,
                "cons_escalated": cons_escalated,
                "total_objects": summary_to_list(alarm.total_objects, ManagedObjectProfile),
                "total_subscribers": summary_to_list(alarm.total_subscribers, SubscriberProfile),
                "total_services": summary_to_list(alarm.total_services, ServiceProfile),
                "tt": None
            }
            if e.create_tt:
                self.stdout.write("    Creating TT\n")
                d = ExtNRITTMap._get_collection().find_one({
                    "managed_object": mo.id
                })
                if not d:
                    self.stdout.write("    @ Cannot find TT System\n")
                    continue
                tt_system = TTSystem.objects.get(id=d["tt_system"])
                tts = tt_system.get_system()
                self.stdout.write("    TT System: %s  Mapped Id: %s\n" % (
                    tt_system.name, d["remote_id"]
                ))
                subject = e.template.render_subject(**ctx)
                body = e.template.render_body(**ctx)
                self.stdout.write("    @ Create network TT\n")
                self.stdout.write("    | Subject: %s\n" % subject)
                self.stdout.write("    |\n")
                self.stdout.write("    | %s\n" % body.replace("\n", "\n    | "))
                tt_id = "<NETWORK TT>"
                ctx["tt"] = "%s:%s" % (tt_system.name, tt_id)
                # alarm.escalate(ctx["tt"], close_tt=e.close_tt)
                if tts.promote_group_tt:
                    self.stdout.write("    Promoting group TT")
                    self.stdout.write("    @ Create Group TT")
                    # Add objects
                    objects = dict(
                        (o.id, o.name)
                        for o in alarm.iter_affected()
                    )
                    remote_ids = dict(
                        (d["managed_object"], d["remote_id"])
                        for d in  ExtNRITTMap._get_collection().find({
                            "managed_object": {
                                "$in": list(objects)
                            }
                        })
                    )
                    for o in objects:
                        if o in remote_ids:
                            self.stdout.write("    @ Add to group TT %s. Remote Id: %s\n" % (
                                objects[o], remote_ids[o]))
                        else:
                            self.stdout.write("    @ Cannot add to group TT %s. Remote id is not found\n" % (
                                objects[o]
                            ))

    def run_alarm(self, alarm):
        AlarmEscalation.watch_escalations(alarm)


if __name__ == "__main__":
    Command().run()
