# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Extract/Transfer/Load commands
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
# Third-party modules
import yaml
import ujson
# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.handler import get_handler
from noc.main.models.remotesystem import RemoteSystem


class Command(BaseCommand):
    CONF = "etc/etl.yml"

    SUMMARY_MASK = "%20s | %8s | %8s | %8s\n"
    CONTROL_MESSAGE = """Summary of %s changes: %d, overload control number: %d\n"""

    def add_arguments(self, parser):
        parser.add_argument(
            "--system",
            action="append",
            help="System to extract"
        )
        subparsers = parser.add_subparsers(dest="cmd")
        # load command
        load_parser = subparsers.add_parser("load")
        load_parser.add_argument(
            "system",
            help="Remote system name"
        )
        load_parser.add_argument(
            "loaders",
            nargs=argparse.REMAINDER,
            help="List of extractor names"
        )
        # check command
        check_parser = subparsers.add_parser("check")
        check_parser.add_argument(
            "system",
            help="Remote system name"
        )
        # diff command
        diff_parser = subparsers.add_parser("diff")
        diff_parser.add_argument(
            "system",
            help="Remote system name"
        )
        diff_parser.add_argument(
            "--summary",
            action="store_true",
            default=False,
            help="Show only summary"
        )
        diff_parser.add_argument(
            "--control-default",
            action="store",
            type=int,
            default=0,
            help="Default control number in summary object"
        )
        diff_parser.add_argument(
            "--control-dict",
            type=str,
            help="Dictionary of control numbers in summary object"
        )
        diff_parser.add_argument(
            "diffs",
            nargs=argparse.REMAINDER,
            help="List of extractor names"
        )
        # extract command
        extract_parser = subparsers.add_parser("extract")
        extract_parser.add_argument(
            "system",
            help="Remote system name"
        )
        extract_parser.add_argument(
            "extractors",
            nargs=argparse.REMAINDER,
            help="List of extractor names"
        )

    def get_config(self):
        with open(self.CONF) as f:
            return yaml.load(f)

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_load(self, *args, **options):
        remote_system = RemoteSystem.get_by_name(options["system"])
        if not remote_system:
            self.die("Invalid remote system: %s" % options["system"])
        remote_system.load(options.get("loaders", []))

    def handle_extract(self, *args, **options):
        remote_system = RemoteSystem.get_by_name(options["system"])
        if not remote_system:
            self.die("Invalid remote system: %s" % options["system"])
        remote_system.extract(options.get("extractors", []))

    def handle_check(self,  *args, **options):
        remote_system = RemoteSystem.get_by_name(options["system"])
        if not remote_system:
            self.die("Invalid remote system: %s" % options["system"])
        n_errors = remote_system.check(self.stdout)
        return 1 if n_errors else 0

    def handle_diff(self, summary=False, *args, **options):
        remote_system = RemoteSystem.get_by_name(options["system"])
        if not remote_system:
            self.die("Invalid remote system: %s" % options["system"])

        diffs = set(options.get("diffs", []))
        if summary:
            self.stdout.write(self.SUMMARY_MASK % (
                "Loader", "New", "Updated", "Deleted"))
        control_dict = {}
        if options["control_dict"]:
            try:
                control_dict = ujson.loads(options["control_dict"])
            except ValueError as e:
                self.die("Failed to parse JSON: %s in %s" % (e, options["control_dict"]))
            except TypeError as e:
                self.die("Failed to parse JSON: %s in %s" % (e, options["control_dict"]))
        chain = remote_system.get_loader_chain()
        for l in chain:
            if diffs and l.name not in diffs:
                continue
            if summary:
                i, u, d = l.check_diff_summary()
                control_num = control_dict.get(l.name, options["control_default"])
                self.stdout.write(self.SUMMARY_MASK % (
                    l.name, i, u, d))
                if control_num:
                    if sum([i, u, d]) >= control_num:
                        self.stdout.write(self.CONTROL_MESSAGE % (l.name, sum([i, u, d]), control_num))
                        self.stderr.write(self.CONTROL_MESSAGE % (l.name, sum([i, u, d]), control_num))
                        n_errors = 1
                        break
            else:
                l.check_diff()
        else:
            n_errors = 0
        return 1 if n_errors else 0

if __name__ == "__main__":
    Command().run()
