# ---------------------------------------------------------------------
# Inject event from JSON files
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import sys
import time
import argparse
from typing import Optional

# Third-party modules
import orjson

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.core.fm.event import Event, EventSeverity, MessageType, Var
from noc.core.etl.models.fmevent import FMEventObject
from noc.core.service.pub import publish
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.profile import GENERIC_PROFILE
from noc.main.models.remotesystem import RemoteSystem


class Command(BaseCommand):
    help = "Inject events from JSON files"

    def add_arguments(self, parser):
        parser.add_argument("-s", "--syslog", action="store_true"),
        parser.add_argument("-o", "--object", dest="objects"),
        parser.add_argument("--remote-system", dest="remote_system"),
        parser.add_argument("args", nargs=argparse.REMAINDER)

    def _usage(self):
        print("./noc inject-event <object name> [<file1> [ .. <fileN>]]")
        sys.exit(0)

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

    def handle(
        self,
        *args,
        syslog: bool = False,
        objects: Optional[str] = None,
        remote_system: Optional[str] = None,
        **options,
    ):
        connect()
        # if len(args) < 1:
        #    self._usage()
        # Get managed object
        if objects:
            objects = ManagedObject.objects.filter(name=objects).first()
            if not objects:
                self.die("Managed Object '%s' is not found" % args[0])
        # Inject syslog messages
        if syslog:
            self.syslog_message(objects, options["syslog"])
            return
        # Load jsons
        if len(args) > 0:
            for f in args:
                self.load_events(f, remote_system=remote_system)
        else:
            self.load_events("/dev/stdin", remote_system=remote_system)

    def load_events(self, path, remote_system: str):
        """Load events from JSON file"""
        # Decode JSON
        rs = RemoteSystem.get_by_name(remote_system)
        with open(path) as f:
            for line in f:
                try:
                    data = orjson.loads(line)
                except ValueError as e:
                    self.die('Failed to decode JSON file "%s": %s' % (path, str(e)))
                e = FMEventObject.model_validate(data)
                e = self.get_fm_event(e, rs)
                publish(orjson.dumps(e.model_dump()), "events.default", partition=0)
        # stream, partition = obj.events_stream_and_partition
        # Load events
        # for e in data:
        #     if e["profile"] != obj.profile.name:
        #         self.stdout.write(
        #             "Profile mismatch in %s: %s != %s %s"
        #             % (path, obj.profile.name, e["profile"], e)
        #         )
        #         continue
        #     raw_vars = {"collector": obj.pool.name}
        #     raw_vars.update(e["raw_vars"])
        #     msg = {
        #         "ts": time.time(),
        #         "object": obj.id,
        #         "data": raw_vars,
        #     }
        #     publish(orjson.dumps(msg), stream, partition=partition)

    def syslog_message(self, obj, msg):
        stream, partition = obj.events_stream_and_partition
        raw_vars = {"source": "syslog", "facility": "23", "severity": "6", "message": msg}
        msg = {"ts": time.time(), "object": obj.id, "data": raw_vars}
        publish(orjson.dumps(msg), stream, partition=partition)


if __name__ == "__main__":
    Command().run()
