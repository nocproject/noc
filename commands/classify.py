# ----------------------------------------------------------------------
# classify
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
from pathlib import Path
import time
from typing import List, Iterable, Set, Union, Dict, Any
from dataclasses import dataclass

# Third-party modules
import orjson

# NOC modules
from noc.core.fm.event import Event, MessageType, Target
from noc.core.fm.enum import EventSource
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.sa.models.profile import Profile
from noc.services.classifier.ruleset import RuleSet


@dataclass
class Stats(object):
    """
    Classification statistics.

    Attributes:
        path: File path.
        total: Total messages.
        classified: Successfully classified message in path.
        duration: Classification duration, in seconds.
    """

    path: Path
    total: int
    classified: int
    duration: float

    def __str__(self) -> str:
        """str() implementation."""
        return (
            f"{self.path}: messages={self.total} classified={self.classified} "
            f"({self.quality * 100.0:.2f}%) "
            f"non-classified={self.non_classified} [{self.duration:.3f}s, {self.rate:.2f} msg/sec]"
        )

    def to_json(self) -> Dict[str, Union[int, float]]:
        return {
            "duration": self.duration,
            "messages": self.total,
            "classified": self.classified,
        }

    @classmethod
    def from_json(cls, path: Path, data: Dict[str, Union[int, float]]) -> "Stats":
        """
        Get Stats from json data.

        Reverse to `to_json`.
        """
        return Stats(
            path=path,
            duration=data["duration"],
            total=data["messages"],
            classified=data["classified"],
        )

    @property
    def non_classified(self) -> int:
        """Non-classified messages."""
        return self.total - self.classified

    @property
    def rate(self) -> float:
        """Classification rate, in msg/s."""
        if self.duration:
            return float(self.total) / self.duration
        return 0.0

    @property
    def quality(self) -> float:
        """Classification quality, in parts."""
        if self.total:
            return float(self.classified) / float(self.total)
        return 0

    def get_comparison(self, other: "Stats") -> str:
        """
        Get comparison report.
        """
        duration_delta = self.duration - other.duration
        r = [f"  Duration: {other.duration:.3f}s -> {self.duration:.3f}s ({duration_delta:.3f}s)"]
        if self.classified == other.classified:
            r.append(f"  Classified: {self.classified} [Unchanged]")
        else:
            delta = self.classified - other.classified
            delta_percent = float(self.classified - other.classified) * 100.0 / float(self.total)
            r.append(
                f"  Classified: {other.classified} -> {self.classified} [{delta} ({delta_percent:.2f}%)]"
            )
        return "\n".join(r)


class Command(BaseCommand):
    help = "Classify events"
    DEFAULT_TARGET = Target.default()
    UNKNOWN_SYSLOG = "Unknown | Syslog"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        # import
        import_parser = subparsers.add_parser("import", help="Parse and import text files")
        import_parser.add_argument("--profile", help="SA Profile", required=True)
        import_parser.add_argument(
            "--output-dir", help="Output directory for results", required=True
        )
        import_parser.add_argument(
            "paths",
            help="Paths for source files",
            nargs=argparse.REMAINDER,
            default=None,
        )
        # refresh
        refresh_parser = subparsers.add_parser(
            "refresh", help="Repeat classification of resulted JSON files"
        )
        refresh_parser.add_argument(
            "paths",
            help="Paths for source JSON-files (directories or files)",
            nargs=argparse.REMAINDER,
            default=None,
        )
        # show
        show_parser = subparsers.add_parser("show", help="Show events from JSON files")
        show_parser.add_argument(
            "--unknown", action="store_true", help="Show only unclassified messages"
        )
        show_parser.add_argument(
            "paths",
            help="Paths for source JSON-files (directories or files)",
            nargs=argparse.REMAINDER,
            default=None,
        )
        # stats
        stats_parser = subparsers.add_parser("stats", help="Show statistics")
        stats_parser.add_argument(
            "paths",
            help="Paths for source JSON-files (directories or files)",
            nargs=argparse.REMAINDER,
            default=None,
        )

    def handle(self, *args, **options):
        cmd = options.pop("cmd")
        return getattr(self, f"handle_{cmd.replace('-', '_')}")(*args, **options)

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
            # priority = 0
            if line.startswith("<"):
                idx = line.find(">")
                if idx == -1:
                    continue
                line = line[idx + 1 :].strip()
            # Get timestamp
            ts = int(time.time())
            # Generate Event
            event = Event(
                ts=ts,
                target=self.DEFAULT_TARGET,
                data=[],
                type=MessageType(source=EventSource.SYSLOG, profile=profile),
                message=line,
            )
            events.append(event)
        return events

    @staticmethod
    def save_output(path: Path, data: Dict[str, Any]) -> None:
        with open(path, "wb") as f:
            f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))

    def process_events(self, profile, ruleset, output_dir, filepath: Path, events: List[Event]):
        """
        Classify events for file located on the path 'filepath'
        """
        msg_cnt, cls_cnt = 0, 0
        time_start = time.perf_counter()
        out_data = []
        ignored_fields = {"target"}
        for event in events:
            raw_vars = {"profile": event.type.profile, "message": event.message}
            rule, r_vars = ruleset.find_rule(event, raw_vars)
            if not rule.name.startswith("Unknown |"):  # EventClass
                cls_cnt += 1
            out_record = {
                "event": event.model_dump(
                    exclude_none=True,
                    exclude_unset=True,
                    exclude_defaults=True,
                    exclude=ignored_fields,
                ),
                "event_class": {"name": rule.event_class_name},
                "vars": r_vars,
            }
            out_data += [out_record]
            msg_cnt += 1
        stats = Stats(
            path=filepath,
            total=msg_cnt,
            classified=cls_cnt,
            duration=time.perf_counter() - time_start,
        )
        out = {
            "$version": 1,
            "input": {
                "profile": profile,
            },
            "stats": stats.to_json(),
            "data": out_data,
        }
        outfile = f"{filepath.name}.json"
        outfile = Path(output_dir, outfile)
        self.save_output(outfile, out)
        self.print(str(stats))

    def refresh_events(self, ruleset: RuleSet, path: Path):
        """
        Repeat classify events for JSON-file located on the path 'filepath'
        """
        with open(path) as f:
            data = orjson.loads(f.read())
        old_stats = Stats.from_json(path, data["stats"])
        msg_cnt, cls_cnt = 0, 0
        time_start = time.perf_counter()
        for d_event in data["data"]:
            event = Event(target=self.DEFAULT_TARGET, **d_event["event"])
            rule, r_vars = ruleset.find_rule(event, {})
            if not rule.name.startswith("Unknown |"):  # EventClass
                cls_cnt += 1
            d_event["event_class"] = {"name": rule.event_class_name}
            d_event["vars"] = r_vars
            msg_cnt += 1
        stats = Stats(
            path=path,
            total=msg_cnt,
            classified=cls_cnt,
            duration=time.perf_counter() - time_start,
        )
        self.save_output(path, data)
        self.print(str(stats))
        self.print(stats.get_comparison(old_stats))

    def _iter_path(self, paths: List[str]) -> Iterable[Path]:
        """
        Iterate all files in path.

        Args:
            paths: List of paths, files or directories.

        Returns:
            Yields Path for every file.
        """
        seen: Set[Path] = set()
        for p in paths:
            path = Path(p)
            if path.is_dir():
                for root, _, files in path.walk():
                    if root.name.startswith("."):
                        continue
                    for f in files:
                        if f.startswith("."):
                            continue
                        f_path = root / f
                        if f_path not in seen:
                            seen.add(f_path)
                            yield f_path
            elif path not in seen:
                seen.add(path)
                yield path

    def get_ruleset(self) -> RuleSet:
        """
        Load ruleset.
        """
        ruleset = RuleSet()
        ruleset.load()
        return ruleset

    def handle_import(
        self,
        paths: List[str],
        profile,
        output_dir,
        **options,
    ):
        connect()
        if not Profile.get_by_name(profile):
            self.die(f"Profile '{profile}' not exists. Process stopped.")
        for path in self._iter_path(paths):
            events = self.parse_syslog_text(profile, path)
            self.process_events(profile, self.get_ruleset(), output_dir, path, events)

    def handle_refresh(
        self,
        paths: List[str],
        **options,
    ):
        connect()
        for path in self._iter_path(paths):
            self.refresh_events(self.get_ruleset(), path)

    def handle_show(self, paths: List[str], unknown: bool = False, **options) -> None:
        for path in self._iter_path(paths):
            with open(path) as fp:
                data = orjson.loads(fp.read())
            for item in data["data"]:
                event = item.get("event")
                if not event:
                    continue
                msg = event.get("message")
                if not msg:
                    continue
                event_class = item.get("event_class")
                if not event_class:
                    continue
                if unknown and event_class["name"] != "Unknown | Syslog":
                    continue
                self.print(msg)

    def handle_stats(self, paths: List[str], **options) -> None:
        for path in self._iter_path(paths):
            with open(path) as fp:
                data = orjson.loads(fp.read())
            stats = Stats.from_json(path, data["stats"])
            self.print(str(stats))


if __name__ == "__main__":
    Command().run()
