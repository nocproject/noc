# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Inject event from JSON files
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
from __future__ import with_statement
import sys
import datetime
import json
import argparse
# NOC modules
from noc.core.management.base import BaseCommand
from noc.sa.models.managedobject import ManagedObject
from noc.fm.models.newevent import NewEvent


class Command(BaseCommand):
    help = "Inject events from JSON files"

    def add_arguments(self, parser):
        parser.add_argument("-s", "--syslog", dest="syslog"),
        parser.add_argument("args",
                            nargs=argparse.REMAINDER)

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
            self.die("Managed Object '%s' is not found" % args[0])
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
                data = json.load(f.read())
            except ValueError as e:
                self.die("Failed to decode JSON file \"%s\": %s" % (
                    path, str(e)))
        # Load events
        for e in data:
            if e["profile"] != obj.profile.name:
                self.stdout.write("Profile mismatch in %s: %s != %s %s" % (
                    path, obj.profile.name, e["profile"], e))
                continue
            ne = NewEvent(
                timestamp=datetime.datetime.now(),
                managed_object=obj,
                raw_vars=e["raw_vars"],
                log=[]
            )
            ne.save()
            self.stdout.write(ne.id)

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
        self.stdout.write(ne.id)

if __name__ == "__main__":
    Command().run()
