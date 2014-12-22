# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Reclassify events
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
from optparse import OptionParser, make_option
import re
import hashlib
from htmlentitydefs import name2codepoint
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.fm.models import ActiveEvent, EventClass, MIB
from noc.lib.nosql import ObjectId
from noc.lib.validators import is_oid
from noc.lib.escape import json_escape, fm_escape

name2codepoint["#39"] = 39
rx_cp = re.compile("&(%s);" % "|".join(name2codepoint))

def unescape(s):
    """
    Unescape HTML string
    """
    return rx_cp.sub(lambda m: unichr(name2codepoint[m.group(1)]), s)


class Command(BaseCommand):
    help = "Manage events"
    option_list = BaseCommand.option_list + (
        make_option("-a", "--action", dest="action",
                    default="show",
                    help="Action: show, reclassify"),
        make_option("-s", "--selector", dest="selector",
                    help="Selector name"),
        make_option("-o", "--object", dest="object",
                    help="Managed Object's name"),
        make_option("-p", "--profile", dest="profile",
                    help="Object's profile"),
        make_option("-e", "--event", dest="event",
                    help="Event ID"),
        make_option("-c", "--class", dest="class",
                    help="Event class name"),
        make_option("-T", "--trap", dest="trap",
                    help="SNMP Trap OID or name"),
        make_option("-S", "--syslog", dest="syslog",
                    help="SYSLOG Message RE"),
        make_option("-d", "--suppress-duplicated", dest="suppress",
                    action="store_true",
                    help="Suppress duplicated subjects"),
        make_option("-l", "--limit", dest="limit", default=0, type="int",
                    help="Limit action to N records")
    )
    
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
                raise CommandError("Object not found: %s" % options["object"])
            c = c.filter(managed_object=o.id)
        if options["selector"]:
            try:
                s = ManagedObjectSelector.objects.get(name=options["selector"])
            except ManagedObjectSelector.DoesNotExist:
                raise CommandError("Selector not found: %s" % options["selector"])
            c = c.filter(managed_object__in=[o.id for o in s.managed_objects])
        if options["class"]:
            o = EventClass.objects.filter(name=options["class"]).first()
            if not o:
                raise CommandError("Event class not found: %s" % options["class"])
            c = c.filter(event_class=o.id)
        if options["trap"]:
            if is_oid(options["trap"]):
                trap_oid = options["trap"]
            else:
                trap_oid = MIB.get_oid(options["trap"])
                if trap_oid is None:
                    raise CommandError("Cannot find OID for %s" % options["trap"])
            c = c.filter(raw_vars__source="SNMP Trap")
        if options["syslog"]:
            try:
                syslog_re = re.compile(options["syslog"], re.IGNORECASE)
            except Exception, why:
                raise CommandError("Invalid RE: %s" % why)
            c = c.filter(raw_vars__source="syslog")
        for e in c:
            if profile:
                if not e.managed_object.profile_name == profile:
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
        except IOError, why:
            print "IO Error: %s" % why

    def _handle(self, *args, **options):
        try:
            handler = getattr(self, "handle_%s" % options["action"])
        except AttributeError:
            raise CommandError("Invalid action: %s" % options["action"])
        events = self.get_events(options)
        handler(options, events)

    def handle_show(self, options, events, show_json=False):
        limit = int(options["limit"])
        to_suppress = options["suppress"]
        seen = set()  # Message hashes
        if show_json:
            print "["
            spool = None
        else:
            print "ID, Object, Class, Subject"
        for e in events:
            subject = unescape(e.get_translated_subject("en"))
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
                    print spool + ","
                s = ["    {"]
                s += ["        \"profile\": \"%s\"," % json_escape(e.managed_object.profile_name)]
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
                print "%s, %s, %s, %s" % (e.id, e.managed_object.name,
                                          e.event_class.name,
                                          subject)
            if limit:
                limit -= 1
                if not limit:
                    break
        if show_json:
            if spool:
                print spool
            print "]"

    def handle_json(self, option, events):
        return self.handle_show(option, events, show_json=True)

    def handle_reclassify(self, options, events):
        limit = int(options["limit"])
        for e in events:
            e.mark_as_new("Reclassification requested via CLI")
            print e.id
            if limit:
                limit -= 1
                if not limit:
                    break
