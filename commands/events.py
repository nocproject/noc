# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Reclassify events
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import print_function
import re
import datetime
import time
import hashlib
from htmlentitydefs import name2codepoint
# Third-party modules
from bson import ObjectId
from pymongo import DeleteMany
from pymongo.errors import DocumentTooLarge
# NOC modules
from noc.core.management.base import BaseCommand
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.profile import Profile
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.fm.models.activeevent import ActiveEvent
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.eventclass import EventClass
from noc.fm.models.mib import MIB
from noc.lib.validators import is_oid
from noc.lib.escape import json_escape


DEFAULT_CLEAN = datetime.timedelta(weeks=4)
CLEAN_WINDOW = datetime.timedelta(weeks=1)

name2codepoint["#39"] = 39
rx_cp = re.compile("&(%s);" % "|".join(name2codepoint))


def unescape(s):
    """
    Unescape HTML string
    """
    return rx_cp.sub(lambda m: unichr(name2codepoint[m.group(1)]), s)


class Command(BaseCommand):
    help = "Manage events"

    def add_arguments(self, parser):
        parser.add_argument("-s", "--selector", dest="selector",
                            help="Selector name"),
        parser.add_argument("-o", "--object", dest="object",
                            help="Managed Object's name"),
        parser.add_argument("-p", "--profile", dest="profile",
                            help="Object's profile"),
        parser.add_argument("-e", "--event", dest="event",
                            help="Event ID"),
        parser.add_argument("-c", "--class", dest="class",
                            help="Event class name"),
        parser.add_argument("-T", "--trap", dest="trap",
                            help="SNMP Trap OID or name"),
        parser.add_argument("-S", "--syslog", dest="syslog",
                            help="SYSLOG Message RE"),
        parser.add_argument("-d", "--suppress-duplicated", dest="suppress",
                            action="store_true",
                            help="Suppress duplicated subjects"),
        parser.add_argument("-l", "--limit", dest="limit", default=0, type=int,
                            help="Limit action to N records")
        subparsers = parser.add_subparsers(dest="cmd")
        subparsers.add_parser("show")
        subparsers.add_parser("json")
        subparsers.add_parser("reclassify")
        clean = subparsers.add_parser("clean")
        clean.add_argument("--before", dest="before",
                           help="Clear events before date")
        clean.add_argument("--force", default=False,
                           action="store_true", help="Really events remove")

    rx_ip = re.compile(r"\d+\.\d+\.\d+\.\d+")
    rx_float = re.compile(r"\d+\.\d+")
    rx_int = re.compile(r"\d+")
    rx_volatile_date = re.compile(r"^.+?(?=%[A-Z])")

    def get_events(self, options):
        """
        Generator returning active events
        """
        c = ActiveEvent.objects.all()
        trap_oid = None
        syslog_re = None
        profile = options["profile"]
        if options["event"]:
            c = c.filter(id=ObjectId(options["event"]))
        if options["object"]:
            try:
                o = ManagedObject.objects.get(name=options["object"])
            except ManagedObject.DoesNotExist:
                self.die("Object not found: %s" % options["object"])
            c = c.filter(managed_object=o.id)
        if options["selector"]:
            try:
                s = ManagedObjectSelector.objects.get(name=options["selector"])
            except ManagedObjectSelector.DoesNotExist:
                self.die("Selector not found: %s" % options["selector"])
            c = c.filter(managed_object__in=[mo.id for mo in s.managed_objects])
        if options["class"]:
            o = EventClass.objects.filter(name=options["class"]).first()
            if not o:
                self.die("Event class not found: %s" % options["class"])
            c = c.filter(event_class=o.id)
        if options["trap"]:
            if is_oid(options["trap"]):
                trap_oid = options["trap"]
            else:
                trap_oid = MIB.get_oid(options["trap"])
                if trap_oid is None:
                    self.die("Cannot find OID for %s" % options["trap"])
            c = c.filter(raw_vars__source="SNMP Trap")
        if options["syslog"]:
            try:
                syslog_re = re.compile(options["syslog"], re.IGNORECASE)
            except Exception as e:
                self.die("Invalid RE: %s" % str(e))
            c = c.filter(raw_vars__source="syslog")
        for e in c:
            if profile:
                if not e.managed_object.profile == Profile[profile]:
                    continue
            if trap_oid:
                if ("source" in e.raw_vars and
                    e.raw_vars["source"] == "SNMP Trap" and
                    "1.3.6.1.6.3.1.1.4.1.0" in e.raw_vars and
                        e.raw_vars["1.3.6.1.6.3.1.1.4.1.0"] == trap_oid):
                    yield e
            elif syslog_re:
                if ("source" in e.raw_vars and
                    e.raw_vars["source"] == "syslog" and
                    "message" in e.raw_vars and
                        syslog_re.search(e.raw_vars["message"])):
                    yield e
            else:
                yield e

    def handle(self, *args, **options):
        try:
            return self._handle(*args, **options)
        except KeyboardInterrupt:
            pass
        except IOError as e:
            self.stdout.write("IO Error: %s" % str(e))

    def _handle(self, *args, **options):
        try:
            handler = getattr(self, "handle_%s" % options["cmd"])
            events = self.get_events(options)
            handler(options, events)
        except AttributeError:
            self.die("Invalid action: %s" % options["action"])

    def handle_show(self, options, events, show_json=False):
        limit = int(options["limit"])
        to_suppress = options["suppress"]
        seen = set()  # Message hashes
        if show_json:
            self.stdout.write("[\n")
            spool = None
        else:
            self.stdout.write("ID, Object, Class, Subject\n")
        for e in events:
            subject = unescape(e.subject)
            if to_suppress:
                # Replace volatile parts
                s = self.rx_volatile_date.sub("", subject)
                s = self.rx_ip.sub("$IP", s)
                s = self.rx_float.sub("$FLOAT", s)
                s = self.rx_int.sub("$INT", s)
                sh = hashlib.sha1(s).hexdigest()
                # Check subject is already seen
                if sh in seen:
                    # Suppress seen
                    continue
                seen.add(sh)
            if show_json:
                if spool:
                    print(spool + ",")
                s = ["    {"]
                s += ["        \"profile\": \"%s\"," % json_escape(e.managed_object.profile.name)]
                s += ["        \"raw_vars\": {"]
                x = []
                vars = e.raw_vars
                keys = []
                lkeys = [k for k in vars.keys()
                         if k not in ("1.3.6.1.2.1.1.3.0",)]
                for k in ("source", "profile", "1.3.6.1.6.3.1.1.4.1.0"):
                    if k in vars:
                        keys += [k]
                        lkeys.remove(k)
                keys += sorted(lkeys)
                for k in keys:
                    if k in ("collector",):
                        continue
                    x += ["            \"%s\": \"%s\"" % (json_escape(k),
                                                          json_escape(vars[k]))]
                s += [",\n".join(x)]
                s += ["        }"]
                s += ["    }"]
                spool = "\n".join(s)
            else:
                self.stdout.write("%s, %s, %s, %s\n" % (e.id, e.managed_object.name,
                                                        e.event_class.name,
                                                        subject))
            if limit:
                limit -= 1
                if not limit:
                    break
        if show_json:
            if spool:
                self.stdout.write(spool)
            print("]")

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

    def handle_clean(self, options, events):
        before = options.get("before")
        if before:
            datetime.datetime.strptime(before, "%Y-%m-%d")
        else:
            self.print("Before is not set, use default")
            before = datetime.datetime.now() - DEFAULT_CLEAN
        force = options.get("force")
        aa = ActiveAlarm._get_collection()
        ah = ArchivedAlarm._get_collection()
        ae = ActiveEvent._get_collection()
        event_ts = ae.find_one({"timestamp": {"$lte": before}}, limit=1, sort=[("timestamp", 1)])
        event_ts = event_ts["timestamp"]
        print("[%s] Cleaned before %s ... \n" % (
            "events", before
        ), end="")
        bulk = []
        window = CLEAN_WINDOW
        while event_ts < before:
            refer_event_ids = []
            for e in [aa, ah]:
                for ee in e.find({"timestamp": {"$gte": event_ts, "$lte": event_ts + CLEAN_WINDOW}},
                                 {"opening_event": 1, "closing_event": 1}):
                    if "opening_event" in ee:
                        refer_event_ids += [ee["opening_event"]]
                    if "closing_event" in ee:
                        refer_event_ids += [ee["closing_event"]]
            try:
                clear_qs = {"timestamp": {"$gte": event_ts, "$lte": event_ts + CLEAN_WINDOW},
                            "_id": {"$nin": refer_event_ids}}
                self.print("Interval: %s, %s; Count: %d" % (event_ts, event_ts + CLEAN_WINDOW, ae.count(clear_qs)))
                bulk += [DeleteMany(clear_qs)]
                event_ts += window
                if window != CLEAN_WINDOW:
                    window = CLEAN_WINDOW
            except DocumentTooLarge:
                window = window // 2
                if window < datetime.timedelta(hours=1):
                    self.die("Too many events for delete in interval %s" % window)
                event_ts -= window
        if force:
            self.print("All data before %s from active events will be Remove..\n" % before)
            for i in reversed(range(1, 10)):
                self.print("%d\n" % i)
                time.sleep(1)
            ae.bulk_write(bulk)


if __name__ == "__main__":
    Command().run()
