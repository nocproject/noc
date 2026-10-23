# ----------------------------------------------------------------------
# Collections manipulation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
from noc.config import config
from pathlib import Path
from contextlib import suppress

# NOC modules
from noc.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        dump_parser = subparsers.add_parser("dump")
        dump_parser.add_argument(
            "section",
            help="Print only config section with Name",
            nargs=argparse.REMAINDER,
            default=None,
        )
        subparsers.add_parser("compile-docs")

    def handle(self, cmd, *args, **options):
        getattr(self, f"handle_{cmd.replace('-', '_')}")(*args, **options)

    def handle_dump(self, section: list[str] | None = None, *args, **options) -> None:
        import yaml

        data = {}
        start = f"{'.'.join(section)}." if section else None
        for name in config:
            if start and not name.startswith(start):
                continue
            current = data
            parts = name.split(".")
            while len(parts) > 1:
                key = parts.pop(0)
                if key not in current:
                    current[key] = {}
                current = current[key]
            with suppress(KeyError):
                current[parts[0]] = config.get_parameter(name)
        self.print(yaml.dump(data, default_flow_style=False))

    def handle_compile_docs(self, *args, **options) -> None:
        import yaml

        r = [
            "# This file is auto-generated",
            "# Do not edit manually!",
            "# Rebuild with:",
            "# ./noc config compile-docs",
        ]
        params = {}
        for name, param in config.iter_params():
            p = {}
            # default
            default = getattr(param, "default", "none")
            if default:
                p["default"] = str(default)
            # choices
            choices = getattr(param, "choices", [])
            if choices:
                p["choices"] = sorted(choices)
            # min
            p_min = getattr(param, "min", None)
            if p_min is not None:
                p["min"] = str(p_min)
            # max
            p_max = getattr(param, "max", None)
            if p_max is not None:
                p["max"] = str(p_max)
            params[name] = p
        r.append(yaml.dump({"params": params}))
        path = Path("docs", "config-reference", "params.yml")
        self.print(f"Writing {path}")
        with open(path, "w") as fp:
            fp.write("\n".join(r))
