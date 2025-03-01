# ----------------------------------------------------------------------
# classify
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
import os
import time

# Third-party modules
import orjson

# NOC modules
from noc.core.comp import smart_text
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

    def handle_parse(
        self,
        paths,
        profile,
        output_dir,
        **options,
    ):
        def process_file(root, file):
            filepath = os.path.join(root, file)
            with open(filepath, "r") as f:
                lines = f.read().splitlines()
            mcnt, ccnt, ucnt = 0, 0, 0
            time1 = time.perf_counter()
            out_data = []
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
                mcnt += 1
                # Get timestamp
                ts = int(time.time())

                # Generate Event
                event = Event(
                    ts=ts,
                    target=Target(address="stub", name="stub"),
                    data=[],
                    message=line,
                )
                # Go to classify event
                rule, r_vars = ruleset.find_rule(event, {})
                # print("rule", rule, type(rule))
                # to be continued...
                out_record = {
                    "event": event.model_dump(),  # должно быть Event
                    "event_class__name": "",
                    "vars": [],
                }
                out_data += [out_record]
            out = {
                "$version": 1,
                "input": {
                    "path": filepath,
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
            outfile = f"{file}.json"
            outfile = os.path.join(output_dir, outfile)
            with open(outfile, "w") as f:
                f.write(smart_text(orjson.dumps(out, option=orjson.OPT_INDENT_2)))
            time2 = time.perf_counter()
            timedelta = time2 - time1
            msg_sec = round(mcnt / timedelta) if timedelta else "--"
            self.print(
                f"{filepath} messages={mcnt} classified={ccnt} unknown={ucnt} () {msg_sec} msg/sec"
            )

        ruleset = RuleSet()
        ruleset.load()
        for path in paths:
            for root, dirs, files in os.walk(path):
                for file in files:
                    process_file(root, file)


if __name__ == "__main__":
    Command().run()
