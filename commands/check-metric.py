# ----------------------------------------------------------------------
# ./noc script
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# Third-party modules
import orjson

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.script.loader import loader as script_loader
from noc.core.profile.loader import loader as profile_loader


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--json",
            action="store_true",
            default=False,
            dest="json_format",
            help="output in JSONEachRow format",
        )
        parser.add_argument("--profile", help="Profile list in JSON format")
        parser.add_argument("--metric", help="Metric list in JSON format")

    def parse_json(self, j):
        try:
            return orjson.loads(j)
        except ValueError as e:
            self.die("Failed to parse JSON: %s" % e)

    def print_csv(self, profile_list, metric_list):
        self.stdout.write(f";{';'.join(m for m in metric_list)};\n")

        for p in profile_list:
            if not p["metrics"]:
                continue
            self.stdout.write(f"{p['name']};")
            for m in metric_list:
                metric = p["metrics"].get(m)
                if metric:
                    self.stdout.write(metric)
                else:
                    self.stdout.write("x")
                self.stdout.write(";")
            self.stdout.write("\n")

    def print_json(self, profile_list, metric_list):
        for p in profile_list:
            if not p["metrics"]:
                continue
            p_name = p["name"]
            metrics = p["metrics"]
            self.stdout.write("%s\n" % orjson.dumps({"name": p_name, **metrics}).decode())

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

    def handle(self, json_format, profile, metric):
        if profile:
            profiles = self.parse_json(profile)
        else:
            profiles = [x for x in profile_loader.iter_profiles()]

        if metric:
            metrics = self.parse_json(metric)
        else:
            metrics = []

        metric_list = []
        profile_list = []

        for p in profiles:
            p_item = {"name": p, "metrics": {}}
            script_name = f"{p}.get_metrics"
            script_class = script_loader.get_script(script_name)
            if not script_class:
                self.die("Failed to load script %s" % script_class)

            service = ServiceStub(pool="")
            # TODO dirty hack
            # Suppress error in /opt/noc/sa/profiles/Ericsson/MINI_LINK/profile.py
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
            except AttributeError:
                continue

            if metrics:
                for m in metrics:
                    if m not in metric_list:
                        metric_list.append(m)
                    if m in scr._mt_map:
                        metric_func_list = scr._mt_map[m]
                        p_item.get("metrics")[m] = self.get_metric_source(metric_func_list)
            else:
                for m in scr._mt_map:
                    if m not in metric_list:
                        metric_list.append(m)
                    metric_func_list = scr._mt_map[m]
                    p_item.get("metrics")[m] = self.get_metric_source(metric_func_list)

            profile_list.append(p_item)

        metric_list.sort()

        if json_format:
            self.print_json(profile_list, metric_list)
        else:
            self.print_csv(profile_list, metric_list)


class ServiceStub(object):
    class ServiceConfig(object):
        def __init__(self, pool, tos=None):
            self.pool = pool
            self.tos = tos

    def __init__(self, pool):
        self.config = self.ServiceConfig(pool=pool)


if __name__ == "__main__":
    Command().run()
