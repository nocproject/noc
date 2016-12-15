# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Extract/Transfer/Load commands
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import argparse
## Third-party modules
import yaml
## NOC modules
from noc.core.management.base import BaseCommand
from noc.core.handler import get_handler


class Command(BaseCommand):
    CONF = "etc/etl.yml"

    SUMMARY_MASK = "%20s | %8s | %8s | %8s\n"

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
            "loaders",
            nargs=argparse.REMAINDER,
            help="List of extractor names"
        )
        # check command
        check_parser = subparsers.add_parser("check")
        # diff command
        diff_parser = subparsers.add_parser("diff")
        diff_parser.add_argument(
            "--summary",
            action="store_true",
            default=False,
            help="Show only summary"
        )
        diff_parser.add_argument(
            "diffs",
            nargs=argparse.REMAINDER,
            help="List of extractor names"
        )
        # extract command
        extract_parser = subparsers.add_parser("extract")
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

    def handle_load(self, system=None, *args, **options):
        from noc.core.etl.loader.chain import LoaderChain

        loaders = set(options.get("loaders", []))
        config = self.get_config()
        for s in config:
            if system and s["system"] not in system:
                continue
            chain = LoaderChain(s["system"])
            for d in s.get("data"):
                chain.get_loader(d["type"])
            # Add & Modify
            for l in chain:
                if loaders and l.name not in loaders:
                    l.load_mappings()
                    continue
                l.load()
                l.save_state()
            # Remove in reverse order
            for l in reversed(list(chain)):
                l.purge()

    def handle_extract(self, system=None, *args, **options):
        extractors = set(options.get("extractors", []))
        config = self.get_config()
        for s in config:
            if system and s["system"] not in system:
                continue
            system_config = s.get("config", {})
            for x_config in reversed(s.get("data", [])):
                config = system_config.copy()
                config.update(x_config.get("config", {}))
                if extractors and x_config["type"] not in extractors:
                    continue
                xc = get_handler(x_config["extractor"])
                extractor = xc(s["system"], config=config)
                extractor.extract()

    def handle_check(self, system=None, *args, **options):
        from noc.core.etl.loader.chain import LoaderChain
        config = self.get_config()
        n_errors = 0
        summary = []
        for s in config:
            if system and s["system"] not in system:
                continue
            chain = LoaderChain(s["system"])
            for d in s.get("data"):
                chain.get_loader(d["type"])
            # Check
            for l in chain:
                n = l.check(chain)
                if n:
                    ss = "%d errors" % n
                else:
                    ss = "OK"
                summary += ["%s.%s: %s" % (s["system"], l.name, ss)]
                n_errors += n
        if summary:
            self.stdout.write("Summary:\n")
            self.stdout.write("\n".join(summary) + "\n")
        return 1 if n_errors else 0

    def handle_diff(self, system=None, summary=False, *args, **options):
        from noc.core.etl.loader.chain import LoaderChain

        diffs = set(options.get("diffs", []))
        config = self.get_config()
        if summary:
            self.stdout.write(self.SUMMARY_MASK % (
                "Loader", "New", "Updated", "Deleted"))
        for s in config:
            if system and s["system"] not in system:
                continue
            chain = LoaderChain(s["system"])
            for d in s.get("data"):
                chain.get_loader(d["type"])
            # Check
            for l in chain:
                if diffs and l.name not in diffs:
                    continue
                if summary:
                    i, u, d = l.check_diff_summary()
                    self.stdout.write(self.SUMMARY_MASK % (
                        l.name, i, u, d))
                else:
                    l.check_diff()

if __name__ == "__main__":
    Command().run()
