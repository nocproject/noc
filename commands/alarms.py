# ---------------------------------------------------------------------
# Manage alarms
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import time
import datetime

# Third-party modules
from pymongo import DeleteMany

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.activealarm import ActiveAlarm

DEFAULT_CLEAN = datetime.timedelta(weeks=4)
CLEAN_WINDOW = datetime.timedelta(weeks=1)


class Command(BaseCommand):
    help = "Manage alarms"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        clean = subparsers.add_parser("clean")
        clean.add_argument("--before", help="Clear events before date")
        clean.add_argument("--before-days", type=int, help="Clear events older than N, days")
        clean.add_argument("--fast", help="Remove by DB Query")
        clean.add_argument(
            "--force", default=False, action="store_true", help="Really events remove"
        )

    def handle(self, cmd, *args, **options):
        connect()
        return getattr(self, f'handle_{cmd.replace("-", "_")}')(*args, **options)

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
