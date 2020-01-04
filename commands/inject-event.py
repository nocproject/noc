# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Inject event from JSON files
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import print_function
import sys
import time
import json
import argparse

# Third-party modules
import bson

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.sa.models.managedobject import ManagedObject
from noc.core.nsq.pub import nsq_pub


class Command(BaseCommand):
    help = "Inject events from JSON files"

    def add_arguments(self, parser):
        parser.add_argument("-s", "--syslog", dest="syslog"),
        parser.add_argument("args", nargs=argparse.REMAINDER)

    def _usage(self):
        print("./noc inject-event <object name> [<file1> [ .. <fileN>]]")
        sys.exit(0)

    def handle(self, *args, **options):
        connect()
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
                data = json.load(f)
            except ValueError as e:
                self.die('Failed to decode JSON file "%s": %s' % (path, str(e)))
        # Load events
        topic = "events.%s" % obj.pool.name
        for e in data:
            if e["profile"] != obj.profile.name:
                self.stdout.write(
                    "Profile mismatch in %s: %s != %s %s"
                    % (path, obj.profile.name, e["profile"], e)
                )
                continue
            msg = {
                "id": str(bson.ObjectId()),
                "ts": time.time(),
                "object": obj.id,
                "data": e["raw_vars"],
            }
            nsq_pub(topic, msg)
            self.stdout.write(msg["id"])

    def syslog_message(self, obj, msg):
        topic = "events.%s" % obj.pool.name
        raw_vars = {"source": "syslog", "facility": "23", "severity": "6", "message": msg}
        msg = {"id": str(bson.ObjectId()), "ts": time.time(), "object": obj.id, "data": raw_vars}
        nsq_pub(topic, msg)
        self.stdout.write(msg["id"])


if __name__ == "__main__":
    Command().run()
