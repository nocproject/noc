# ----------------------------------------------------------------------
# escalation command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
import operator
import time

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.fm.models.alarmescalation import AlarmEscalation
from noc.fm.models.utils import get_alarm
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.sa.models.serviceprofile import ServiceProfile
from noc.crm.models.subscriberprofile import SubscriberProfile
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.core.defer import call_later


class Command(BaseCommand):
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        #
        check_parser = subparsers.add_parser("check")
        check_parser.add_argument(
            "check_alarms", nargs=argparse.REMAINDER, help="Checks alarms escalation"
        )
        #
        run_parser = subparsers.add_parser("run")
        run_parser.add_argument(
            "--limit", type=int, default=0, help="Limit escalations (per minute)"
        )
        run_parser.add_argument(
            "run_alarms", nargs=argparse.REMAINDER, help="Run alarm escalations"
        )
        #
        close_parser = subparsers.add_parser("close")
        close_parser.add_argument(
            "close_alarms", nargs=argparse.REMAINDER, help="Close escalated TT"
        )

    def handle(self, cmd, *args, **options):
        connect()
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_check(self, check_alarms=None, *args, **kwargs):
        check_alarms = check_alarms or []
        for a_id in check_alarms:
            alarm = get_alarm(a_id)
            if alarm:
                self.check_alarm(alarm)
            else:
                self.print("ERROR: Alarm %s is not found. Skipping" % alarm)

    def handle_run(self, run_alarms=None, limit=0, *args, **kwargs):
        run_alarms = run_alarms or []
        if limit:
            delay = 60.0 / limit
        for a_id in run_alarms:
            alarm = get_alarm(a_id)
            if alarm and alarm.status == "A":
                self.print("Sending alarm %s to escalator" % alarm.id)
                self.run_alarm(alarm)
                if limit:
                    time.sleep(delay)
            elif alarm:
                self.print("ERROR: Alarm %s is cleared. Skipping" % alarm)
            else:
                self.print("ERROR: Alarm %s is not found. Skipping" % alarm)

    def handle_close(self, close_alarms=None, *args, **kwargs):
        close_alarms = close_alarms or []
        for a_id in close_alarms:
            alarm = get_alarm(a_id)
            if alarm and alarm.status == "A" and alarm.escalation_tt:
                self.print("Sending TT close for alarm %s to escalator" % alarm.id)
                call_later(
                    "noc.services.escalator.escalation.notify_close",
                    scheduler="escalator",
                    pool=alarm.managed_object.escalator_shard,
                    alarm_id=alarm.id,
                    tt_id=alarm.escalation_tt,
                    subject="Closed",
                    body="Closed",
                    notification_group_id=None,
                    close_tt=False,
                )
            elif alarm:
                self.print("ERROR: Alarm %s is not escalated. Skipping" % alarm)
            else:
                self.print("ERROR: Alarm %s is not found. Skipping" % alarm)

    def check_alarm(self, alarm):
        def summary_to_list(summary, model):
            r = []
            for k in summary:
                p = model.get_by_id(k.profile)
                if not p or getattr(p, "show_in_summary", True) is False:
                    continue
                r += [{"profile": p.name, "summary": k.summary}]
            return sorted(r, key=lambda x: -x["summary"])

        def iter_consequences(alarm):
            """
            Generator yielding all consequences alarm
            """
            for ac in [ArchivedAlarm, ActiveAlarm]:
                for a in ac.objects.filter(root=alarm.id):
                    yield a
                    yield from a.iter_consequences()

        def iter_affected(alarm):
            """
            Generator yielding all affected managed objects
            """
            seen = {alarm.managed_object}
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
        self.print("-" * 72)
        self.print(f"Alarm Id : {alarm.id}  Time: {alarm.timestamp}")
        self.print(f"Class    : {alarm.alarm_class.name}")
        self.print(f"Object   : {mo.name}  Platform: {mo.platform}  IP: {mo.address}")
        c = mo.administrative_domain
        adm_domains = [c]
        while c.parent:
            c = c.parent
            adm_domains.insert(0, c)
        self.print(
            "Adm. Dom.: %s (%s)"
            % (" | ".join(c.name for c in adm_domains), " | ".join(str(c.id) for c in adm_domains))
        )
        escalations = list(
            AlarmEscalation.objects.filter(alarm_classes__alarm_class=alarm.alarm_class.id)
        )
        if not escalations:
            self.print("@ No matched escalations")
            return
        for esc in escalations:
            self.print(f"[Chain: {esc.name}]")
            if alarm.root:
                self.print(f"    @ Not a root cause (Root Id: {alarm.root})")
                continue
            for e in esc.escalations:
                self.print(f"    [After {e.delay}s]")
                # Check administrative domain
                if e.administrative_domain and e.administrative_domain.id not in alarm.adm_path:
                    self.print(
                        f"    @ Administrative domain mismatch ({e.administrative_domain.id} not in {alarm.adm_path})"
                    )
                    continue
                # Check severity
                if e.min_severity and alarm.severity < e.min_severity:
                    self.print(f"    @ Severity mismatch: {alarm.severity} < {e.min_severity}")
                    continue
                # Check resource group
                if e.resource_group and str(e.resource_group.id) not in mo.effective_service_groups:
                    self.print(f"    @ ResourceGroup mismatch ({e.resource_group.name} required)")
                    continue
                # Check time pattern
                if e.time_pattern and not e.time_pattern.match(alarm.timestamp):
                    self.print(f"    @ Time pattern mismatch ({e.time_pattern.name} required)")
                    continue
                # Render escalation message
                if not e.template:
                    self.print("    @ No escalation template")
                    continue
                # Check whether consequences has escalations
                cons_escalated = sorted(iter_escalated(alarm), key=operator.attrgetter("timestamp"))
                affected_objects = sorted(iter_affected(alarm), key=operator.attrgetter("name"))
                #
                ctx = {
                    "alarm": alarm,
                    "affected_objects": affected_objects,
                    "cons_escalated": cons_escalated,
                    "total_objects": summary_to_list(alarm.total_objects, ManagedObjectProfile),
                    "total_subscribers": summary_to_list(
                        alarm.total_subscribers, SubscriberProfile
                    ),
                    "total_services": summary_to_list(alarm.total_services, ServiceProfile),
                    "tt": None,
                }
                if e.create_tt:
                    self.print("    Creating TT")
                    tt_system = mo.tt_system
                    if not tt_system:
                        self.print("    @ No TT System. Cannot escalate")
                    elif not mo.can_escalate():
                        self.print("    @ Escalation disabled by policy")
                    else:
                        tts = tt_system.get_system()
                        self.print(
                            "    TT System: %s  Mapped Id: %s" % (tt_system.name, mo.tt_system_id)
                        )
                        subject = e.template.render_subject(**ctx)
                        body = e.template.render_body(**ctx)
                        self.print("    @ Create network TT")
                        self.print("    | Subject: %s" % subject)
                        self.print("    |")
                        self.print("    | %s" % body.replace("\n", "\n    | "))
                        tt_id = "<NETWORK TT>"
                        ctx["tt"] = "%s:%s" % (tt_system.name, tt_id)
                        # alarm.escalate(ctx["tt"], close_tt=e.close_tt)
                        if tts.promote_group_tt:
                            self.print("    Promoting group TT")
                            self.print("    @ Create Group TT")
                            # Add objects
                            for o in alarm.iter_affected():
                                if o.can_escalate(depended=True):
                                    if o.tt_system == mo.tt_system:
                                        self.print(
                                            f"    @ Add to group TT {o.name}. Remote Id: {o.tt_system_id}"
                                        )
                                    else:
                                        self.print(
                                            f"    @ Cannot add to group TT {o.name}. Belongs to other TT system"
                                        )
                                else:
                                    self.print(
                                        f"    @ Cannot add to group TT {o.name}. Escalations are disabled"
                                    )
                if e.notification_group:
                    if mo.can_notify():
                        subject = e.template.render_subject(**ctx)
                        body = e.template.render_body(**ctx)
                        self.print(
                            f"    @ Sending notification to group '{e.notification_group.name}'"
                        )
                        self.print("    | Subject: %s" % subject)
                        self.print("    |")
                        self.print("    | %s" % body.replace("\n", "\n    | "))
                    else:
                        self.print("    @ Notification disabled by policy")
                if e.stop_processing:
                    self.print("    @ Stop processing")
                    break

    def run_alarm(self, alarm):
        AlarmEscalation.watch_escalations(alarm)


if __name__ == "__main__":
    Command().run()
