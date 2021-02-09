# ---------------------------------------------------------------------
# Inject event from JSON files
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import sys
import time
import json
import argparse

# Third-party modules
import orjson

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.sa.models.managedobject import ManagedObject
from noc.core.service.pub import publish


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
        stream, partition = obj.events_stream_and_partition
        # Load events
        for e in data:
            if e["profile"] != obj.profile.name:
                self.stdout.write(
                    "Profile mismatch in %s: %s != %s %s"
                    % (path, obj.profile.name, e["profile"], e)
                )
                continue
            raw_vars = {"collector": obj.pool.name}
            raw_vars.update(e["raw_vars"])
            msg = {
                "ts": time.time(),
                "object": obj.id,
                "data": raw_vars,
            }
            publish(orjson.dumps(msg), stream, partition=partition)

    def syslog_message(self, obj, msg):
        stream, partition = obj.events_stream_and_partition
        raw_vars = {"source": "syslog", "facility": "23", "severity": "6", "message": msg}
        msg = {"ts": time.time(), "object": obj.id, "data": raw_vars}
        publish(orjson.dumps(msg), stream, partition=partition)


if __name__ == "__main__":
    Command().run()
