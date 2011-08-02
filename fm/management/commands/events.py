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
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.sa.models import ManagedObject
from noc.fm.models import ActiveEvent, EventClass, MIB
from noc.lib.nosql import ObjectId
from noc.lib.validators import is_oid


class Command(BaseCommand):
    help = "Manage events"
    option_list = BaseCommand.option_list + (
        make_option("-a", "--action", dest="action",
                    default="show",
                    help="Action: show, reclassify"),
        #make_option("-s", "--selector", dest="selector",
        #            help="Selector name"),
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
                    help="SYSLOG Message RE")
    )

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
                syslog_re = re.compile(options["syslog"])
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
            handler = getattr(self, "handle_%s" % options["action"])
        except AttributeError:
            raise CommandError("Invalid action: %s" % options["action"])
        events = self.get_events(options)
        handler(options, events)

    def handle_show(self, options, events):
        print "ID, Object, Class, Subject"
        for e in events:
            print "%s, %s, %s, %s" % (e.id, e.managed_object.name,
                                      e.event_class.name,
                                      e.get_translated_subject("en"))

    def handle_reclassify(self, options, events):
        for e in events:
            e.mark_as_new("Reclassification requested via CLI")
            print e.id
