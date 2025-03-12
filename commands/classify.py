# ----------------------------------------------------------------------
# classify
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
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
from noc.core.fm.event import Event, MessageType, Target
from noc.core.fm.enum import EventSource
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.sa.models.profile import Profile
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
        refresh = subparsers.add_parser("refresh", help="Repeat classify of resulted JSON files")
        refresh.add_argument(
            "paths",
            help="Paths for source JSON-files (directories or files)",
            nargs=argparse.REMAINDER,
            default=None,
        )

    def handle(self, *args, **options):
        connect()
        cmd = options.pop("cmd")
        return getattr(self, f'handle_{cmd.replace("-", "_")}')(*args, **options)

    def parse_syslog_text(self, profile: str, filepath: Path) -> List[Event]:
        """
        Parse events from syslog-format file located on the path 'filepath'
        """
        with open(filepath, "r") as f:
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
            message_type = MessageType(source=EventSource.SYSLOG, profile=profile)
            event = Event(
                ts=ts,
                target=Target(address="stub", name="stub"),
                data=[],
                type=message_type,
                message=line,
            )
            events += [event]
        return events

    def process_events(self, profile, ruleset, output_dir, filepath: Path, events: List[Event]):
        """
        Classify events for file located on the path 'filepath'
        """
        msg_cnt, cls_cnt = 0, 0
        time_start = time.perf_counter()
        out_data = []
        for event in events:
            raw_vars = {"profile": event.type.profile, "message": event.message}
            rule, r_vars = ruleset.find_rule(event, raw_vars)
            if not rule.name.startswith("Unknown |"):  # EventClass
                cls_cnt += 1
            out_record = {
                "event": event.model_dump(),
                "event_class__name": rule.event_class.name,
                "vars": r_vars,
            }
            out_data += [out_record]
            msg_cnt += 1
        time_delta = time.perf_counter() - time_start
        out = {
            "$version": 1,
            "input": {
                "path": filepath.as_posix(),
                "profile": profile,
            },
            "stats": {
                "duration": time_delta,
                "messages": msg_cnt,
                "classified": cls_cnt,
                "unknown": msg_cnt - cls_cnt,
            },
            "data": out_data,
        }
        outfile = f"{filepath.name}.json"
        outfile = Path(output_dir, outfile)
        with open(outfile, "wb") as f:
            f.write(orjson.dumps(out, option=orjson.OPT_INDENT_2))
        cls_percent = round((cls_cnt / msg_cnt) * 100, 1) if msg_cnt else "--"
        msg_sec = round(msg_cnt / time_delta) if time_delta else "--"
        self.print(
            f"{filepath} messages={msg_cnt} classified={cls_cnt} unknown={msg_cnt - cls_cnt} "
            f"(classified {cls_percent}%) {msg_sec} msg/sec"
        )

    def refresh_events(self, ruleset, filepath: Path):
        """
        Repeat classify events for JSON-file located on the path 'filepath'
        """
        with open(filepath) as f:
            data = orjson.loads(f.read())
        old_cls_cnt = data["stats"]["classified"]
        old_unk_cnt = data["stats"]["unknown"]
        msg_cnt, cls_cnt = 0, 0
        time_start = time.perf_counter()
        for d_event in data["data"]:
            event = Event(**d_event["event"])
            rule, r_vars = ruleset.find_rule(event, {})
            if not rule.name.startswith("Unknown |"):  # EventClass
                cls_cnt += 1
            msg_cnt += 1
        time_delta = time.perf_counter() - time_start
        cls_percent = round((cls_cnt / msg_cnt) * 100, 1) if msg_cnt else "--"
        msg_sec = round(msg_cnt / time_delta) if time_delta else "--"
        cls_delta = cls_cnt - old_cls_cnt
        unk_delta = msg_cnt - cls_cnt - old_unk_cnt
        cls_percent_delta = round((cls_delta / msg_cnt) * 100, 1) if msg_cnt else "--"
        cls_delta = f"+{cls_delta}" if cls_delta >= 0 else f"-{cls_delta}"
        unk_delta = f"+{unk_delta}" if unk_delta >= 0 else f"-{unk_delta}"
        if isinstance(cls_percent_delta, float):
            cls_percent_delta = (
                f"+{cls_percent_delta}" if cls_percent_delta >= 0 else f"-{cls_percent_delta}"
            )
        self.print(
            f"{filepath} messages={msg_cnt} classified={cls_cnt} ({cls_delta}) "
            f"unknown={msg_cnt - cls_cnt} ({unk_delta}) (classified {cls_percent}% "
            f"({cls_percent_delta}%)) {msg_sec} msg/sec"
        )

    def handle_parse(
        self,
        paths,
        profile,
        output_dir,
        **options,
    ):
        if not Profile.get_by_name(profile):
            self.die(f"Profile '{profile}' not exists. Process stopped.")
        ruleset = RuleSet()
        ruleset.load()
        for path in paths:
            for root, dirs, files in os.walk(path):
                for file in files:
                    filepath = Path(root, file)
                    events = self.parse_syslog_text(profile, filepath)
                    self.process_events(profile, ruleset, output_dir, filepath, events)

    def handle_refresh(
        self,
        paths,
        **options,
    ):
        ruleset = RuleSet()
        ruleset.load()
        for path in paths:
            path = Path(path)
            filepaths = []
            if path.is_dir():
                for fp in sorted(path.iterdir()):
                    if fp.is_file():
                        filepaths += [fp]
            if path.is_file():
                filepaths = [path]
            for filepath in filepaths:
                self.refresh_events(ruleset, filepath)


if __name__ == "__main__":
    Command().run()
