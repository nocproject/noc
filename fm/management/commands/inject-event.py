# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Inject event from JSON files
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
from __future__ import with_statement
import sys
import datetime
from optparse import OptionParser, make_option
## Django modules
from django.core.management.base import BaseCommand, CommandError
from django.utils import simplejson
## NOC modules
from noc.sa.models import ManagedObject
from noc.fm.models import NewEvent


class Command(BaseCommand):
    help = "Inject events from JSON files"
    option_list = BaseCommand.option_list + (
        make_option("-s", "--syslog", dest="syslog"),
    )
    
    def _usage(self):
        print "./noc inject-event <object name> [<file1> [ .. <fileN>]]"
        sys.exit(0)

    def handle(self, *args, **options):
        if len(args) < 1:
            self._usage()
        # Get managed object
        try:
            o = ManagedObject.objects.get(name=args[0])
        except ManagedObject.DoesNotExist:
            raise CommandError("Managed Object '%s' is not found" % args[0])
        # Inject syslog messages
        if options["syslog"]:
            self.syslog_message(o, options["syslog"])
            return
        # Load jsons
        if len(args) > 1:
            for f in args[1:]:
                self.load_events(o, f)
        else:
            self.load_events(o, "/dev/stdin")

    def load_events(self, obj, path):
        """
        Load events from JSON file
        """
        # Decode JSON
        with open(path) as f:
            try:
                data = simplejson.JSONDecoder().decode(f.read())
            except ValueError, why:
                raise CommandError("Failed to decode JSON file \"%s\": %s" % (
                    path, why))
        # Load events
        for e in data:
            if e["profile"] != obj.profile_name:
                print "Profile mismatch in %s: %s != %s %s" % (
                    path, obj.profile_name, e["profile"], e)
                continue
            ne = NewEvent(
                timestamp=datetime.datetime.now(),
                managed_object=obj,
                raw_vars=e["raw_vars"],
                log=[]
            )
            ne.save()
            print ne.id
    
    def syslog_message(self, obj, msg):
        raw_vars = {
            "source": "syslog",
            "facility": "23",
            "severity": "6",
            "message": msg
        }
        ne = NewEvent(
            timestamp=datetime.datetime.now(),
            managed_object=obj,
            raw_vars=raw_vars,
            log=[]
        )
        ne.save()
        print ne.id
