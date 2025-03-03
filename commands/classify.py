# ----------------------------------------------------------------------
# classify
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
import os
from pathlib import Path
import time
from typing import List

# Third-party modules
import orjson

# NOC modules
from noc.core.fm.event import Event, Target
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.services.classifier.ruleset import RuleSet


class Command(BaseCommand):
    help = "Classify events"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        parse = subparsers.add_parser("parse", help="Parse textual syslog files")
        parse.add_argument("--profile", help="SA Profile", required=True)
        parse.add_argument("--output-dir", help="Output directory for results", required=True)
        parse.add_argument(
            "paths",
            help="Paths for source files",
            nargs=argparse.REMAINDER,
            default=None,
        )

    def handle(self, *args, **options):
        connect()
        cmd = options.pop("cmd")
        return getattr(self, f'handle_{cmd.replace("-", "_")}')(*args, **options)

    def parse_syslog_text(self, path: Path) -> List[Event]:
        with open(path, "r") as f:
            lines = f.read().splitlines()
        events = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Parse priority
            priority = 0
            if line.startswith("<"):
                idx = line.find(">")
                if idx == -1:
                    continue
                try:
                    priority = int(line[1:idx])
                except ValueError:
                    pass
                line = line[idx + 1 :].strip()
            # Get timestamp
            ts = int(time.time())
            # Generate Event
            event = Event(
                ts=ts,
                target=Target(address="stub", name="stub"),
                data=[],
                message=line,
            )
            events += [event]
        return events

    def process_events(self, profile, ruleset, output_dir, filepath: Path, events: List[Event]):
        mcnt, ccnt, ucnt = 0, 0, 0
        time_start = time.perf_counter()
        out_data = []
        for event in events:
            # Go to classify event
            rule, r_vars = ruleset.find_rule(event, {})
            # print("rule", rule, type(rule))
            # to be continued...
            out_record = {
                "event": event.model_dump(),
                "event_class__name": "",
                "vars": [],
            }
            out_data += [out_record]
            mcnt += 1
        out = {
            "$version": 1,
            "input": {
                "path": filepath.as_posix(),
                "profile": profile,
            },
            "stats": {
                "duration": 0,
                "messages": mcnt,
                "classified": 0,
                "unknown": 0,
            },
            "data": out_data,
        }
        outfile = f"{filepath.name}.json"
        outfile = Path(output_dir, outfile)
        with open(outfile, "wb") as f:
            f.write(orjson.dumps(out, option=orjson.OPT_INDENT_2))
        time_delta = time.perf_counter() - time_start
        msg_sec = round(mcnt / time_delta) if time_delta else "--"
        self.print(
            f"{filepath} messages={mcnt} classified={ccnt} unknown={ucnt} () {msg_sec} msg/sec"
        )

    def handle_parse(
        self,
        paths,
        profile,
        output_dir,
        **options,
    ):
        ruleset = RuleSet()
        ruleset.load()
        for path in paths:
            for root, dirs, files in os.walk(path):
                for file in files:
                    filepath = Path(root, file)
                    events = self.parse_syslog_text(filepath)
                    self.process_events(profile, ruleset, output_dir, filepath, events)


if __name__ == "__main__":
    Command().run()
