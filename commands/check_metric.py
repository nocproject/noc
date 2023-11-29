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
from noc.core.script.loader import loader as script_loader
from noc.core.profile.loader import loader as profile_loader

from noc.sa.profiles.Generic.get_metrics import MetricConfig

class Command(BaseCommand):
    def add_arguments(self, parser):
        # parser.add_argument("script", nargs=1, help="Script name")
        parser.add_argument("--profile", help="Profile list in JSON format")
        parser.add_argument("--metric", help="Metric list in JSON format")
        # parser.add_argument(
        #     "arguments", nargs=argparse.REMAINDER, help="Arguments passed to script"
        # )

    def parse_json(self, j):
        try:
            return orjson.loads(j)
        except ValueError as e:
            self.die("Failed to parse JSON: %s" % e)

    def print_csv(self, profile_list, metric_list):
        self.stdout.write(f";{';'.join(m for m in metric_list)};\n")

        for p in profile_list:
            self.stdout.write(f"{p['name']};")
            for m in metric_list:
                metric = p["metrics"].get(m)
                if metric:
                    self.stdout.write(metric)
                else:
                    self.stdout.write("x")
                self.stdout.write(";")
            self.stdout.write("\n")

    def get_metric_source(self, func_list):
        res = ""
        for mf in func_list:
            func_name = mf.__name__
            metric_src = "S" if func_name.startswith("get_snmp_json") else "C"
            
            if (metric_src == "S" and res == "C") or (metric_src == "C" and res == "S"):
                res = "SC"
            if not res:
                res = metric_src
        return res

    def handle(
        self,
        profile,
        metric
        # arguments,
        # *args,
        # **options,
    ):
        # self.stdout.write(f"{'='*16}\n")
        # self.stdout.write(f"{profile}\n")
        # self.stdout.write(f"{'-'*16}\n")
        # self.stdout.write(f"{metric}\n")
        # self.stdout.write(f"{'='*16}\n")

        if profile:
            profiles = self.parse_json(profile)
        else:
            # self.stdout.write(f"{'='*16}\n")
            # for x in profile_loader.iter_profiles():
            #     self.stdout.write(f"{x}\n")
            profiles = [x for x in profile_loader.iter_profiles()]
            # self.stdout.write(f"{'='*16}\n")

        if metric:
            metrics = self.parse_json(metric)
        else:
            metrics = []
        # object_metrics = [MetricConfig(**m) for m in metrics]

        # self.stdout.write(f"{'='*16}\n")
        # self.stdout.write(f"{profiles}\n")
        # self.stdout.write(f"{'-'*16}\n")
        # self.stdout.write(f"{metrics}\n")
        # self.stdout.write(f"{'='*16}\n")

        metric_list = []
        profile_list = []

        for p in profiles:
            p_item = {"name": p, "metrics": {}}
            script_name = f"{p}.get_metrics"
            script_class = script_loader.get_script(script_name)
            if not script_class:
                self.die("Failed to load script %s" % script_class)

            service = ServiceStub(pool="")
            # Suppress any errors
            try:
                scr = script_class(
                    service=service,
                    credentials={},
                    capabilities=[],
                    args=[],
                    version={},
                    timeout=3600,
                    name=script_name,
                )
            except:
                continue

            # supported_metrics = []
            # unsupported_metrics = []
            if metrics:
                for m in metrics:
                    if m not in metric_list:
                        metric_list.append(m)
                    if m in scr._mt_map:
                        p_item.get("metrics")[m] = "C"
            else:
                for m in scr._mt_map:
                    metric_func_list = scr._mt_map[m]
                    if m not in metric_list:
                        metric_list.append(m)
                    p_item.get("metrics")[m] = self.get_metric_source(metric_func_list)

            # for m in metrics:
            #     if m not in metric_list:
            #         metric_list.append(m)
                
            #     if m in scr._mt_map:
            #         # supported_metrics.append(m)
                    
            #     # else:
            #     #     unsupported_metrics.append(m)

            profile_list.append(p_item)
        
        # self.stdout.write(f"{metric_set}\n")
        # self.stdout.write(f"{profile_list}\n")

        metric_list.sort()
        self.print_csv(profile_list, metric_list)

            # self.stdout.write(f"supported:   {supported_metrics}\n")
            # self.stdout.write(f"unsupported: {unsupported_metrics}\n")


        # args = self.get_script_args(arguments)
        # # Load script
        # self.stdout.write(f"{script}")
        # script = script[0]
        # script_class = loader.get_script(script)
        # if not script_class:
        #     self.die("Failed to load script %s" % script_class)

        # metrics = args.get("metrics")
        # if not metrics:
        #     self.die("args must have metrics")

        # object_metrics = [MetricConfig(**m) for m in metrics]

        # service = ServiceStub(pool="")
        # scr = script_class(
        #     service=service,
        #     credentials={},
        #     capabilities=[],
        #     args=args,
        #     version={},
        #     timeout=3600,
        #     name=script,
        # )

        # supported_metrics = []
        # unsupported_metrics = []
        # for m in object_metrics:
        #     if m.metric in scr._mt_map:
        #         supported_metrics.append(m.metric)
        #     else:
        #         unsupported_metrics.append(m.metric)

        # self.stdout.write(f"supported:   {supported_metrics}\n")
        # self.stdout.write(f"unsupported: {unsupported_metrics}\n")

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
