# ----------------------------------------------------------------------
# ./noc script
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import argparse
import re

# Third-party modules
import orjson

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.script.loader import loader

from noc.sa.profiles.Generic.get_metrics import MetricConfig

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("script", nargs=1, help="Script name")
        parser.add_argument(
            "arguments", nargs=argparse.REMAINDER, help="Arguments passed to script"
        )

    def handle(
        self,
        script,
        arguments,
        *args,
        **options,
    ):
        args = self.get_script_args(arguments)
        # Load script
        self.stdout.write(f"{script}")
        script = script[0]
        script_class = loader.get_script(script)
        if not script_class:
            self.die("Failed to load script %s" % script_class)

        metrics = args.get("metrics")
        if not metrics:
            self.die("args must have metrics")

        object_metrics = []
        for m in metrics:
            object_metrics.append(MetricConfig(**m))

        service = ServiceStub(pool="")
        scr = script_class(
            service=service,
            credentials={},
            capabilities=[],
            args=args,
            version={},
            timeout=3600,
            name=script,
        )

        supported_metrics = []
        unsupported_metrics = []
        for m in object_metrics:
            if m.metric in scr._mt_map:
                supported_metrics.append(m.metric)
            else:
                unsupported_metrics.append(m.metric)

        self.stdout.write(f"supported:   {supported_metrics}\n")
        self.stdout.write(f"unsupported: {unsupported_metrics}\n")

    rx_arg = re.compile(r"^(?P<name>[a-zA-Z][a-zA-Z0-9_]*)(?P<op>:?=@?)(?P<value>.*)$")

    def get_script_args(self, arguments):
        """
        Parse arguments and return script's
        """

        def read_file(path):
            if not os.path.exists(path):
                self.die("Cannot open file '%s'" % path)
            with open(path) as f:
                return f.read()

        def parse_json(j):
            try:
                return orjson.loads(j)
            except ValueError as e:
                self.die("Failed to parse JSON: %s" % e)

        args = {}
        for a in arguments:
            match = self.rx_arg.match(a)
            if not match:
                self.die("Malformed parameter: '%s'" % a)
            name, op, value = match.groups()
            if op == "=":
                # Set parameter
                args[name] = value
            elif op == "=@":
                # Read from file
                args[name] = read_file(value)
            elif op == ":=":
                # Set to JSON value
                args[name] = parse_json(value)
            elif op == ":=@":
                # Set to JSON value from a file
                args[name] = parse_json(read_file(value))
        return args

class ServiceStub(object):
    class ServiceConfig(object):
        def __init__(self, pool, tos=None):
            self.pool = pool
            self.tos = tos

    def __init__(self, pool):
        self.config = self.ServiceConfig(pool=pool)

if __name__ == "__main__":
    Command().run()
