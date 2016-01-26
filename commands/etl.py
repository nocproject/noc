# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Extract/Transfer/Load commands
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
import yaml
## NOC modules
from noc.core.management.base import BaseCommand
from noc.lib.solutions import get_solution


class Command(BaseCommand):
    CONF = "etc/etl.yml"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        # load command
        load_parser = subparsers.add_parser("load")
        # check command
        check_parser = subparsers.add_parser("check")
        # diff command
        diff = subparsers.add_parser("diff")
        # extract command
        extract_parser = subparsers.add_parser("extract")

    def get_config(self):
        with open(self.CONF) as f:
            return yaml.load(f)

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_load(self, *args, **options):
        from noc.core.etl.loader.chain import LoaderChain

        config = self.get_config()
        for system in config:
            chain = LoaderChain(system["system"])
            for d in system.get("data"):
                chain.get_loader(d["type"])
            # Add & Modify
            for l in chain:
                l.load()
                l.save_state()
            # Remove in reverse order
            for l in reversed(list(chain)):
                l.purge()

    def handle_extract(self, *args, **options):
        config = self.get_config()
        for system in config:
            system_config = system.get("config", {})
            for x_config in system.get("data", []):
                config = system_config.copy()
                config.update(x_config.get("config", {}))
                xc = get_solution(x_config["extractor"])
                extractor = xc(system["system"], config=config)
                extractor.extract()

    def handle_check(self, *args, **options):
        from noc.core.etl.loader.chain import LoaderChain
        config = self.get_config()
        n_errors = 0
        summary = []
        for system in config:
            chain = LoaderChain(system["system"])
            for d in system.get("data"):
                chain.get_loader(d["type"])
            # Check
            for l in chain:
                n = l.check(chain)
                if n:
                    s = "%d errors" % n
                else:
                    s = "OK"
                summary += ["%s.%s: %s" % (system["system"], l.name, s)]
                n_errors += n
        if summary:
            self.stdout.write("Summary:\n")
            self.stdout.write("\n".join(summary) + "\n")
        return 1 if n_errors else 0

    def handle_diff(self, *args, **options):
        from noc.core.etl.loader.chain import LoaderChain
        config = self.get_config()
        for system in config:
            chain = LoaderChain(system["system"])
            for d in system.get("data"):
                chain.get_loader(d["type"])
            # Check
            for l in chain:
                l.check_diff()

if __name__ == "__main__":
    Command().run()
