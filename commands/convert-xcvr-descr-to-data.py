# ----------------------------------------------------------------------
# ./noc script
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# Third-party modules
import orjson

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.script.loader import loader as script_loader
from noc.core.profile.loader import loader as profile_loader
from noc.core.mongo.connection import connect
from noc.inv.models.objectmodel import ObjectModel

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

    wav_patterns = [
        re.compile(r"(?:\s|^)(?P<rx>\d+)\s+rx\s+(?P<tx>\d+)\s+tx(?:\s|$)"),
        re.compile(r"(?:\s|^)(?P<tx>\d+)\s+tx\s+(?P<rx>\d+)\s+rx(?:\s|$)"),
        re.compile(r"(?:\s|^)rx (?P<rx>\d+) tx (?P<tx>\d+)(?:\s|$)"),
        re.compile(r"(?:\s|^)tx/rx: (?P<tx>\d+)/(?P<rx>\d+)nm(?:\s|$)"),

        re.compile(r"(?:\s|^)rx-(?P<rx>\d+)/tx-(?P<tx>\d+)(?:\s|$)"),
        re.compile(r"(?:\s|^)tx-(?P<tx>\d+)/rx-(?P<rx>\d+)(?:\s|$)"),
        
        re.compile(r"(?:\s|^)rx(?P<rx>\d+)/tx(?P<tx>\d+)(?:\s|$)"),
        re.compile(r"(?:\s|^)tx(?P<tx>\d+)/rx(?P<rx>\d+)(?:\s|$)"),
        re.compile(r"(?:\s|^)(?P<tx>\d+)-tx/(?P<rx>\d+)-rx(?:\s|$)"),
        re.compile(r"(?:\s|^)(?P<tx>\d+)nm-tx/(?P<rx>\d+)nm-rx(?:\s|$)"),

        re.compile(r"(?:\s|^)wavelength: (?P<tx>\d+)-(?P<rx>\d+) nm(?:\s|$)"),
        re.compile(r"(?:\s|^)wavelength:(?P<tx>\d+) nm(?:\s|$)"),

        re.compile(r"(?:\s|^)(?P<txrx>\d+) txrx(?:\s|$)"),
        re.compile(r"(?:\s|^)tx (?P<tx>\d+)(?:\s|$)"),
        re.compile(r"(?:\s|^)rx (?P<rx>\d+)(?:\s|$)"),

        re.compile(r"(?:\s|^)(?P<tx>\d+)nm(?:\s|$)"),
        re.compile(r"(?:\s|^)(?P<tx>\d+)-nm(?:\s|$)"),
        re.compile(r"(?:\s|^)(?P<tx>\d+) nm(?:\s|$)"),
        re.compile(r"(?:\s|^)(?P<tx>1310)(?:\s|$)"),
        re.compile(r"(?:\s|^)(?P<tx>1550)(?:\s|$)"),
        re.compile(r"(?:\s|^)(?P<tx>1\d{3})(?:\s|$)"),
    ]

    dist_patterns = [
        re.compile(r"(?::|;|\s|^)(?P<km>\d+)km(?::|;|\s|$)"),

        re.compile(r"(?::|;|\s|^)(?P<km>\d+)\s+km(?::|;|\s|$)"),

        re.compile(r"(?::|;|\s|^)(?P<m>\d+)m(?::|;|\s|$)"),
        re.compile(r"(?::|;|\s|^)(?P<m>\d+)\s+meter(?::|;|\s|$)"),

        re.compile(r"(?::|;|\s|^)(?P<m>\d+)\s+m(?::|;|\s|$)"),
    ]

    connector_patterns = [
        re.compile(r"(?:\s|^)(?P<connector>lc)(?:\s|$)"),
        re.compile(r"(?:\s|^)(?P<connector>sc)(?:\s|$)"),
    ]

    transceiver_patterns = [
        re.compile(r"(?:\s|^)10gbase-(?P<ttype10g>cr|sr|srl|lr|lrm|cx4|lx4|er|zr)(?:/|\s|$)"),
        re.compile(r"(?:\s|^)sfp\+\s+(?P<ttype10g>cr|sr|srl|lr|lrm|cx4|lx4|er|zr)(?:\s|$)"),
        re.compile(r"(?:\s|^)10g\s+(?P<ttype10g>cr|sr|srl|lr|lrm|cx4|lx4|er|zr)(?:\s|$)"),
        re.compile(r"(?:\s|^)xfp\s+(?P<ttype10g>cr|sr|srl|lr|lrm|cx4|lx4|er|zr)(?:\s|$)"),

        re.compile(r"(?:\s|^)1000base-(?P<ttype1g>sx|t)(?:\s|$)"),
        re.compile(r"(?:\s|^)sfp\s+(?P<ttype1g>sx|t)(?:\s|$)"),


        re.compile(r"(?:\s|^)(?P<ttype1g>lh/lx)\s+transceiver(?:\s|$)"),
    ]

    bidi_patterns = [
        re.compile(r"(?:\s|^)sfp wdm(?:\s|$)"),
        re.compile(r"(?:\s|^)sfp\+ wdm(?:\s|$)"),
        re.compile(r"(?:\s|^)wdm-1g\S+(?:\s|$)"),

        re.compile(r"(?:\s|^)bi-directional(?:\s|$)"),
        re.compile(r"(?:\s|^)bidirectional(?:\s|$)"),
        re.compile(r"(?:\s|^)wdm(?:\s|$)"),

        re.compile(r"(?:\s|^)gepon(?:\s|$)"),
        re.compile(r"(?:\s|^)epon(?:\s|$)"),
        re.compile(r"(?:\s|^)gpon(?:\s|$)"),
    ]

    def handle(self, json_format, profile, metric):
        connect()
        for o in ObjectModel.objects.filter(name={"$regex": ".*Transceiver.*"}):
            description = o.description.strip()
            description = description.lower()
            description = description.replace("(", "")
            description = description.replace(")", "")
            description = description.replace(",", "")
            self.stdout.write("%s\n" % o)
            self.stdout.write("    %s\n" % description)

            for p in self.connector_patterns:
                match = p.search(description)
                if match:
                    if "connector" in match.groupdict():
                        self.stdout.write("        CONNECTOR: %s\n" % match.group("connector"))

            for p in self.transceiver_patterns:
                match = p.search(description)
                if match:
                    if "ttype10g" in match.groupdict():
                        self.stdout.write("        TTYPE10G: %s\n" % match.group("ttype10g"))

                    if "ttype1g" in match.groupdict():
                        self.stdout.write("        TTYPE1G: %s\n" % match.group("ttype1g"))

            isbidi = False
            for p in self.bidi_patterns:
                match = p.search(description)
                if match:
                    isbidi = True
                    break

            tx = 0
            rx = 0
            for p in self.wav_patterns:
                match = p.search(description)
                if match:
                    if not rx and "rx" in match.groupdict():
                        rx = match.group("rx")
                        self.stdout.write("        RX: %s\n" % rx)
                        if tx:
                            break
                    if not tx and "tx" in match.groupdict():
                        tx = match.group("tx")
                        self.stdout.write("        TX: %s\n" % tx)
                        if rx:
                            break
                    if "txrx" in match.groupdict():
                        tx = match.group("txrx")
                        rx = match.group("txrx")
                        self.stdout.write("        TX: %s\n" % tx)
                        self.stdout.write("        RX: %s\n" % rx)
                        break

            # if tx and rx and tx != rx:
            #     isbidi = True

            for p in self.dist_patterns:
                match = p.search(description)
                if match:
                    if "km" in match.groupdict():
                        self.stdout.write("        Distance: %skm\n" % match.group("km"))
                        break
                    if "m" in match.groupdict():
                        self.stdout.write("        Distance: %sm\n" % match.group("m"))
                        break

            self.stdout.write("        BIDI: %s\n" % isbidi)

            self.stdout.write("\n")
            
            continue

            parts = description.split()
            next_parts = parts[1:] + [""]
            prev_parts = [""] + parts
            # self.stdout.write("%s\n" % parts)
            # self.stdout.write("%s\n" % prev_parts)
            for p_now, p_prev, p_next in zip(parts, prev_parts, next_parts):
                # self.stdout.write("now %s\n" % p_now)
                # self.stdout.write("prev %s\n" % p_prev)
                # self.stdout.write("next %s\n" % p_next)
                if p_now == "rx":
                    if p_prev.isdigit():
                        self.stdout.write("    0    RX Wavelength: %s\n" % p_prev)
                    else:
                        if p_next.isdigit():
                            self.stdout.write("    0    RX Wavelength: %s\n" % p_prev)

                if p_now == "tx":
                    if p_prev.isdigit():
                        self.stdout.write("    0    TX Wavelength: %s\n" % p_prev)
                    else:
                        if p_next.isdigit():
                            self.stdout.write("    0    TX Wavelength: %s\n" % p_prev)

                if p_now == "nm":
                    if p_prev.isdigit():
                        self.stdout.write("    5    TX Wavelength: %s\n" % p_prev)
                    else:
                        nm_parts = p_prev.split("/")
                        if len(nm_parts) == 2:
                            for p in nm_parts:
                                if "rx-" in p:
                                    p = p.replace("rx-", "")
                                    if p.isdigit():
                                        self.stdout.write("    7    RX Wavelength: %s\n" % p)
                                if "tx-" in p:
                                    p = p.replace("tx-", "")
                                    if p.isdigit():
                                        self.stdout.write("    7    TX Wavelength: %s\n" % p)

                if p_now.endswith("nm") and p_now != "nm":
                    nm = p_now.replace("nm", "")
                    if nm.isdigit():
                        self.stdout.write("    10    TX Wavelength: %s\n" % nm)
                    else:
                        nm_parts = nm.split("/")
                        if len(nm_parts) == 2:
                            self.stdout.write("    15    TX Wavelength: %s\n" % nm_parts[0])
                            self.stdout.write("    15    RX Wavelength: %s\n" % nm_parts[1])

                if p_now.endswith("km") and p_now != "km":
                    km = p_now.replace("km", "")
                    if km.isdigit():
                        self.stdout.write("        Distance: %s km\n" % km)

                if p_now.endswith("m") and p_now != "m":
                    km = p_now.replace("m", "")
                    if km.isdigit():
                        self.stdout.write("        Distance: %s m\n" % km)
        return
        # if profile:
        #     profiles = self.parse_json(profile)
        # else:
        #     profiles = [x for x in profile_loader.iter_profiles()]

        # if metric:
        #     metrics = self.parse_json(metric)
        # else:
        #     metrics = []

        # metric_list = []
        # profile_list = []

        # for p in profiles:
        #     p_item = {"name": p, "metrics": {}}
        #     script_name = f"{p}.get_metrics"
        #     script_class = script_loader.get_script(script_name)
        #     if not script_class:
        #         self.die("Failed to load script %s" % script_class)

        #     service = ServiceStub(pool="")
        #     # TODO dirty hack
        #     # Suppress error in /opt/noc/sa/profiles/Ericsson/MINI_LINK/profile.py
        #     try:
        #         scr = script_class(
        #             service=service,
        #             credentials={},
        #             capabilities=[],
        #             args=[],
        #             version={},
        #             timeout=3600,
        #             name=script_name,
        #         )
        #     except AttributeError:
        #         continue

        #     if metrics:
        #         for m in metrics:
        #             if m not in metric_list:
        #                 metric_list.append(m)
        #             if m in scr._mt_map:
        #                 metric_func_list = scr._mt_map[m]
        #                 p_item.get("metrics")[m] = self.get_metric_source(metric_func_list)
        #     else:
        #         for m in scr._mt_map:
        #             if m not in metric_list:
        #                 metric_list.append(m)
        #             metric_func_list = scr._mt_map[m]
        #             p_item.get("metrics")[m] = self.get_metric_source(metric_func_list)

        #     profile_list.append(p_item)

        # metric_list.sort()

        # if json_format:
        #     self.print_json(profile_list, metric_list)
        # else:
        #     self.print_csv(profile_list, metric_list)


class ServiceStub(object):
    class ServiceConfig(object):
        def __init__(self, pool, tos=None):
            self.pool = pool
            self.tos = tos

    def __init__(self, pool):
        self.config = self.ServiceConfig(pool=pool)


if __name__ == "__main__":
    Command().run()
