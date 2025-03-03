# ---------------------------------------------------------------------
# Manage alarms
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import time
import datetime
import argparse
from typing import Optional, Dict, Any, List

# Third-party modules
import orjson
from pymongo import DeleteMany
from pydantic import BaseModel

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.activealarm import ActiveAlarm
from noc.sa.models.managedobject import ManagedObject
from noc.core.service.loader import get_service
from noc.core.validators import is_ipv4

DEFAULT_CLEAN = datetime.timedelta(weeks=4)
CLEAN_WINDOW = datetime.timedelta(weeks=1)


class AlarmItem(BaseModel):
    op: str = "raise"  # raise, clear, set_status
    managed_object: str
    alarm_class: str = "NOC | Managed Object | Ping Failed"
    reference: Optional[str] = None
    vars: Optional[Dict[str, Any]] = None
    severity: Optional[int] = None
    delay: int = 1
    labels: Optional[List[str]] = None
    status: bool = False

    def get_message(self):
        r = {
            "$op": self.op,
            "managed_object": self.managed_object,
            "reference": self.reference,
        }
        if self.op == "clear":
            return r
        if self.op == "raise" and self.alarm_class:
            r["alarm_class"] = self.alarm_class
        if self.op == "raise" and self.severity:
            r["severity"] = int(self.severity)
        if self.op == "set_status":
            return {
                "$op": "set_status",
                "statuses": [
                    {
                        "timestamp": datetime.datetime.now(),
                        "managed_object": self.managed_object,
                        "status": self.status,
                        "labels": self.labels,
                    }
                ],
            }
        if self.vars:
            r["vars"] = self.vars
        if self.labels:
            r["labels"] = self.labels
        return r


class AlarmConfig(BaseModel):
    repeat: Optional[int] = None  # repeat Alarm Item
    delay: int = 1  # wait interval
    alarms: List[AlarmItem]


class Command(BaseCommand):
    help = "Manage alarms"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        clean = subparsers.add_parser("clean", help="Clean alarm")
        clean.add_argument("--before", help="Clear alarm before date")
        clean.add_argument("--before-days", type=int, help="Clear alarm older than N, days")
        clean.add_argument("--fast", help="Remove by DB Query (not escalation check)")
        clean.add_argument(
            "--force", default=False, action="store_true", help="Really alarms remove"
        )
        send_raise = subparsers.add_parser("raise", help="Send alarm raise message to Correlator")
        send_raise.add_argument("--managed-object", help="ManagedObject ")
        send_raise.add_argument("--alarm-class", help="Alarm Class")
        send_raise.add_argument("--reference", help="Alarm Reference")
        send_raise.add_argument("--vars", dest="a_vars", help="Alarm vars")
        send_raise.add_argument("--labels", help="Alarm labels")
        send_close = subparsers.add_parser("close", help="Send alarm clear message to Correlator")
        send_close.add_argument("--managed-object", help="ManagedObject ")
        send_close.add_argument("--alarm-class", help="Alarm Class")
        send_close.add_argument("--reference", help="Alarm Reference")
        send_close.add_argument("--message", help="Close message")
        run_test = subparsers.add_parser("run-test", help="Send Correlator messages from file")
        run_test.add_argument("args", nargs=argparse.REMAINDER)

    def handle(self, *args, **options):
        connect()
        cmd = options.pop("cmd")
        return getattr(self, f'handle_{cmd.replace("-", "_")}')(*args, **options)

    def resolve_object(self, managed_object: str) -> Optional[ManagedObject]:
        """
        Resolve managed_object
        :param managed_object:
        :return:
        """
        if managed_object.isdigit():
            mo = ManagedObject.get_by_id(int(managed_object))
        elif is_ipv4(managed_object):
            mo = ManagedObject.objects.filter(address=managed_object).first()
        else:
            mo = ManagedObject.objects.filter(name=managed_object).first()
        return mo

    def handle_close(
        self,
        managed_object,
        alarm_class: Optional[str] = None,
        reference: Optional[str] = None,
        message: Optional[str] = None,
    ):
        mo = self.resolve_object(managed_object)
        if not mo:
            self.die(f"Unknown ManagedObject {managed_object}")
        if not reference and alarm_class:
            ac = AlarmClass.get_by_name(alarm_class)
            if not ac:
                self.print(f"Unknown Alarm Class {ac.name}")
                return
            reference = self.get_default_reference(mo, ac)
        msg = {
            "$op": "clear",
            "reference": reference,
            "timestamp": datetime.datetime.now().isoformat(),
            "message": message,
        }
        self.publish(mo, msg)

    def handle_raise(
        self,
        managed_object: str,
        alarm_class: str,
        reference: Optional[str] = None,
        a_vars: Optional[str] = None,
        labels: Optional[str] = None,
    ):
        mo = self.resolve_object(managed_object)
        if not mo:
            self.die(f"Unknown ManagedObject {managed_object}")
        ac = AlarmClass.get_by_name(alarm_class)
        if not ac:
            self.print(f"Unknown Alarm Class {ac.name}")
            return
        if a_vars:
            a_vars = orjson.loads(a_vars)
        msg = {
            "$op": "raise",
            "reference": reference or self.get_default_reference(mo, ac, a_vars),
            "timestamp": datetime.datetime.now().isoformat(),
            "managed_object": str(mo.id),
            "alarm_class": ac.name,
            "labels": labels.split(",") if labels else [],
        }
        # Render vars
        if a_vars:
            msg["vars"] = a_vars
        self.publish(mo, msg)

    def handle_run_test(self, *args, **options):
        for path in args:
            with open(path) as f:
                for line in f:
                    try:
                        data = orjson.loads(line)
                        ac = AlarmConfig(**data)
                    except ValueError as e:
                        self.die(f'Failed to decode JSON file "{path}": {str(e)}')
                    time.sleep(ac.delay)
                    for rr in range(0, ac.repeat or 1):
                        for r in ac.alarms:
                            mo = self.resolve_object(r.managed_object)
                            r.managed_object = str(mo.id)
                            r.reference = r.reference or self.get_default_reference(
                                managed_object=mo,
                                alarm_class=AlarmClass.get_by_name(r.alarm_class),
                                vars=r.vars,
                            )
                            if not mo:
                                continue
                            self.publish(managed_object=mo, msg=r.get_message())
                            time.sleep(r.delay)

    @staticmethod
    def get_default_reference(
        managed_object: ManagedObject,
        alarm_class: AlarmClass,
        vars: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate default reference for event-based alarms.
        Reference has a form of

        ```
        e:<mo id>:<alarm class id>:<value1>:...:<value N>
        ```

        :param managed_object: Managed Object instance
        :param alarm_class: Alarm Class instance
        :param vars: Variables
        :returns: Reference string
        """
        if not vars:
            return f"e:{managed_object.id}:{alarm_class.id}"
        var_suffix = ":".join(
            str(vars.get(n, "")).replace("\\", "\\\\").replace(":", r"\:")
            for n in alarm_class.reference
        )
        return f"e:{managed_object.id}:{alarm_class.id}:{var_suffix}"

    def publish(self, managed_object: ManagedObject, msg):
        svc = get_service()
        stream, partition = managed_object.alarms_stream_and_partition
        self.print(f"Send message: {msg}")
        svc.publish(orjson.dumps(msg), stream=stream, partition=partition)

    def handle_clean(
        self,
        alarms=None,
        before=None,
        before_days=None,
        force=False,
        fast=False,
        alarm_class=None,
        **options,
    ):
        conditions = {}
        if alarm_class:
            conditions["alarm_class"] = AlarmClass.get_by_name(alarm_class).id
        if before:
            conditions["timestamp"] = {"$lte": datetime.datetime.strptime(before, "%Y-%m-%d")}
        elif before_days:
            conditions["timestamp"] = {
                "$lte": datetime.datetime.now() - datetime.timedelta(days=before_days)
            }
        # else:
        #    self.print("Before is not set, use default. Clean ALL")
        #    before = datetime.datetime.now() - DEFAULT_CLEAN

        aac = ActiveAlarm._get_collection()
        count = aac.count_documents(conditions)
        self.print(f"[alarms] Cleaned with condition {conditions or 'ALL'}: {count} ... \n", end="")
        if force:
            self.print(f"All data {count} from active alarms will be Remove..\n")
            for i in reversed(range(1, 10)):
                self.print("%d\n" % i)
                time.sleep(1)
            if fast:
                aac.bulk_write([DeleteMany(conditions)])
                return
            for aa in ActiveAlarm.objects.filter(**conditions):
                aa.clear_alarm("By manual")
        else:
            self.print("For Really remove data run commands with --force argument")


if __name__ == "__main__":
    Command().run()
