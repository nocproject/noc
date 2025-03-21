# ---------------------------------------------------------------------
# Reclassify events
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import datetime
import argparse
import time
from typing import Optional
from html.entities import name2codepoint

# Third-party modules
import orjson

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.core.etl.models.fmevent import FMEventObject
from noc.core.fm.event import Event, EventSeverity, MessageType, Var, EventSource, Target
from noc.core.service.pub import publish
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.profile import GENERIC_PROFILE
from noc.main.models.remotesystem import RemoteSystem
from noc.fm.models.eventclassificationrule import EventClassificationRule
from noc.services.classifier.ruleset import RuleSet


DEFAULT_CLEAN = datetime.timedelta(weeks=4)
CLEAN_WINDOW = datetime.timedelta(weeks=1)

name2codepoint["#39"] = 39
rx_cp = re.compile("&(%s);" % "|".join(name2codepoint))


def unescape(s):
    """
    Unescape HTML string
    """
    return rx_cp.sub(lambda m: chr(name2codepoint[m.group(1)]), s)


class Command(BaseCommand):
    help = "Manage events"

    def add_arguments(self, parser):
        # parser.add_argument("-s", "--selector", dest="selector", help="Selector name"),
        # parser.add_argument("-s", "--resource-group", dest="resource_group", help="Group"),
        # parser.add_argument("-o", "--object", dest="object", help="Managed Object's name"),
        # parser.add_argument("-p", "--profile", dest="profile", help="Object's profile"),
        # parser.add_argument("-e", "--event", dest="event", help="Event ID"),
        # parser.add_argument("-c", "--class", dest="class", help="Event class name"),
        # parser.add_argument("-T", "--trap", dest="trap", help="SNMP Trap OID or name"),
        # parser.add_argument("-S", "--syslog", dest="syslog", help="SYSLOG Message RE"),
        # parser.add_argument(
        #     "-d",
        #     "--suppress-duplicated",
        #     dest="suppress",
        #     action="store_true",
        #     help="Suppress duplicated subjects",
        # ),
        # parser.add_argument(
        #     "-l", "--limit", dest="limit", default=0, type=int, help="Limit action to N records"
        # )
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        subparsers.add_parser("show")
        subparsers.add_parser("reclassify")
        subparsers.add_parser("export")
        inject_event = subparsers.add_parser("inject-event")
        inject_event.add_argument("--syslog"),
        inject_event.add_argument("-o", "--object", dest="objects"),
        inject_event.add_argument("--remote-system", dest="remote_system"),
        inject_event.add_argument("args", nargs=argparse.REMAINDER)
        test_rule = subparsers.add_parser("test-rule")
        test_rule.add_argument(
            "rules",
            help="Rules ids list",
            # required=True,
            nargs=argparse.REMAINDER,
        )
        # test_rule.add_argument("-S", "--syslog", dest="syslog", help="SYSLOG Message RE"),

    rx_ip = re.compile(r"\d+\.\d+\.\d+\.\d+")
    rx_float = re.compile(r"\d+\.\d+")
    rx_int = re.compile(r"\d+")
    rx_volatile_date = re.compile(r"^.+?(?=%[A-Z])")

    def handle(self, cmd, *args, **options):
        connect()
        return getattr(self, "handle_%s" % cmd.replace("-", "_"))(*args, **options)

    def handle_json(self, option, events):
        return self.handle_show(option, events, show_json=True)

    @staticmethod
    def handle_reclassify(options, events):
        limit = int(options["limit"])
        for e in events:
            e.mark_as_new("Reclassification requested via CLI")
            print(e.id)
            if limit:
                limit -= 1
                if not limit:
                    break

    def handle_inject_event(
        self,
        *args,
        syslog: Optional[str] = None,
        object: Optional[str] = None,
        remote_system: Optional[str] = None,
        **options,
    ):
        # Inject syslog messages
        if object:
            object = ManagedObject.objects.filter(name=object).first()
            if not object:
                self.die(f"Managed Object '{object}' is not found")
        if syslog:
            self.syslog_message(object, syslog)
            return
        # Load jsons
        if len(args) > 0:
            for f in args:
                self.load_events(f, remote_system=remote_system)
        else:
            self.load_events("/dev/stdin", remote_system=remote_system)

    @staticmethod
    def get_fm_event(e: FMEventObject, remote_system: RemoteSystem) -> Event:
        """
        Register FM Event for send to classifier

        Args:
            e: timestamp
            remote_system:
        """
        if not e.data and not e.message:
            raise AttributeError("Unknown message data. Set data or message")
        severity = EventSeverity(int(e.severity)) if e.severity else EventSeverity.INDETERMINATE
        event = Event(
            ts=e.ts,
            remote_id=e.id,
            remote_system=remote_system.name,
            target=e.object.get_target(),
            type=MessageType(
                severity=severity if not e.is_cleared else EventSeverity.CLEARED,
                event_class=e.event_class,
                profile=GENERIC_PROFILE,
            ),
            data=[Var(name=d.name, value=d.value) for d in e.data],
            message=e.message,
            labels=e.labels,
        )
        event.target.pool = e.object.pool or "default"
        return event

    def load_events(self, path, remote_system: str):
        """Load event from JSON File"""
        rs = RemoteSystem.get_by_name(remote_system)
        with open(path) as f:
            for line in f:
                try:
                    data = orjson.loads(line)
                except ValueError as e:
                    self.die(f"Failed to decode JSON file '{path}': {str(e)}")
                e = FMEventObject.model_validate(data)
                e = self.get_fm_event(e, rs)
                publish(orjson.dumps(e.model_dump()), "events.default", partition=0)

    def syslog_message(self, obj: ManagedObject, msg: str):
        stream, partition = obj.events_stream_and_partition
        e = Event(
            ts=int(time.time()),
            target=Target(
                name=obj.name,
                address=obj.address,
                id=str(obj.id),
            ),
            type=MessageType(
                source=EventSource.SYSLOG,
                facility=str(23),
                severity=EventSeverity(4),
            ),
            message=msg,
        )
        publish(orjson.dumps(e), stream, partition=partition)

    def handle_test_rule(self, rules, **kwargs):
        ruleset = RuleSet()
        ruleset.load()
        event_class_rules = EventClassificationRule.objects.filter(id__in=rules)
        for event_class_rule in event_class_rules:
            for event, v in event_class_rule.iter_cases():
                rule, e_vars = ruleset.find_rule(event, v)
                if rule is None:
                    self.print(
                        f"[{event_class_rule.name}] Testing with result: Cannot find matching rule"
                    )
                self.print(
                    f"[{event_class_rule.name}] Testing with result: {rule.name}: '{rule.event_class}': {e_vars}"
                )
                assert (
                    rule.event_class == event_class_rule.event_class
                ), f"Mismatched event class '{rule.event_class.name}' vs '{event_class_rule.event_class.name}'"
                var_ctx = {"message": event.message}
                var_ctx |= v
                var_ctx |= e_vars
                for t in rule.vars_transform or []:
                    t.transform(e_vars, var_ctx)
                if "interface__ifindex" in e_vars and "interface_mock" in v:
                    e_vars["interface"] = v.pop("interface_mock")
                elif "interface__ifindex" in e_vars:
                    assert (
                        "interface_mock" in e_vars
                    ), "interface_mock Required for ifindex transform test"
                try:
                    vv = ruleset.eval_vars(event, rule.event_class, e_vars)
                    self.print("End variables: ", vv)
                except Exception as e:
                    self.print(e)
                    self.print("End variables: ", var_ctx)


if __name__ == "__main__":
    Command().run()
