# ----------------------------------------------------------------------
# ./noc script
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
import os
import errno

# Third-party modules
import orjson

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.script.loader import loader as script_loader
from noc.core.profile.loader import loader as profile_loader
from noc.core.mongo.connection import connect
from noc.inv.models.objectmodel import ObjectModel, ModelAttr
from noc.inv.models.object import ObjectAttr

from noc.core.collection.base import Collection
from noc.models import get_model

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            default=False,
            dest="apply_mongo",
            help="store changes to mongo",
        )
        parser.add_argument(
            "--backup-dir",
            dest="backup_dir",
            help="save collections backup to specified directory before apply",
        )
        parser.add_argument(
            "--output-dir",
            dest="output_dir",
            help="save changed collections to specified directory",
        )

    def gen_filename(self, output_dir: str, o: ObjectModel)-> str:
        name_parts = o.name.split("|")
        name_parts = [s.strip().replace(" ", "_") for s in name_parts]
        name_parts[-1] += ".json"

        file_name = os.path.join(output_dir, *name_parts)

        return file_name

    def save_json(self, o_dir, o) -> None:
        fname = self.gen_filename(o_dir, o)
        dir_name = os.path.dirname(fname)

        try:
            os.makedirs(dir_name)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        with open(fname, "w") as f:
            f.write(o.to_json())

        return

    def save_json(self, o_dir, path_, o) -> None:
        # fname = self.gen_filename(o_dir, o)
        # dir_name = os.path.dirname(fname)

        fname = os.path.join(o_dir, *path_.split("/")[2:])
        dir_name = os.path.dirname(fname)

        self.stdout.write("%s\n" % fname)

        try:
            os.makedirs(dir_name)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        with open(fname, "w") as f:
            f.write(orjson.dumps(o).decode("UTF-8"))

        return

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
        re.compile(r"(?:\s|^)wavelength: (?P<tx>\d+)tx(?:\s|$)"),

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

    xwdm_patterns = [
        re.compile(r"(?:\s|^)cwdm(?:\s|$)"),
    ]

    xpon_patterns = [
        re.compile(r"(?:\s|^)gpon(?:\s|$)"),
        re.compile(r"(?:\s|^)gepon(?:\s|$)"),
        re.compile(r"(?:\s|^)epon(?:\s|$)"),
        re.compile(r"(?:\s|^)epon(?:\S|$)"),
    ]

    def load_collections_from_files(self):
        items = {}
        cm = get_model("inv.ObjectModel")
        cn = cm._meta["json_collection"]
        c = Collection(cn)

        # self.stdout.write("%s\n" % c.get_path())

        cdata = c.get_items()
        for x in cdata:
            if "transceiver" in cdata[x].data["name"].lower():
                # self.stdout.write("%s\n" % cdata[x].path)
                # self.stdout.write("%s\n" % cdata[x].data)
                items[x] = cdata[x]
        
        return items


        # for p in c.get_path():
        #     for root, dirs, files in os.walk(p):
        #         for cf in files:
        #             if not cf.endswith(".json"):
        #                 continue
        #             fp = os.path.join(root, cf)
        #             if not "Transceiver" in fp:
        #                 continue
        #             self.stdout.write("%s\n" % fp)
        #             with open(fp) as f:
        #                 data = f.read()
        #             try:
        #                 jdata = orjson.loads(data)
        #             except ValueError as e:
        #                 raise ValueError("Error load %s: %s" % (fp, e))
        

    def parse_description(self, description):
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

        isxwdm = False
        for p in self.xwdm_patterns:
            match = p.search(description)
            if match:
                isxwdm = True
                break

        isxpon = False
        for p in self.xpon_patterns:
            match = p.search(description)
            if match:
                isxpon = True
                break

        tx = 0
        rx = 0
        for p in self.wav_patterns:
            match = p.search(description)
            if match:
                if not rx and "rx" in match.groupdict():
                    rx = int(match.group("rx"))
                    if tx:
                        break
                if not tx and "tx" in match.groupdict():
                    tx = int(match.group("tx"))
                    if rx:
                        break
                if "txrx" in match.groupdict():
                    tx = int(match.group("txrx"))
                    rx = int(match.group("txrx"))
                    break

        # if tx and rx and tx != rx:
        #     isbidi = True

        distance = 0
        for p in self.dist_patterns:
            match = p.search(description)
            if match:
                if "km" in match.groupdict():
                    distance = int(match.group("km")) * 1000
                    break
                if "m" in match.groupdict():
                    distance = int(match.group("m"))
                    break

        if not (rx and tx) and isxpon:
            tx = 1490
            rx = 1310

        if distance:
            self.stdout.write("        Distance: %sm\n" % distance)
        if rx:
            self.stdout.write("        RX: %s\n" % rx)
        if tx:
            self.stdout.write("        TX: %s\n" % tx)
        self.stdout.write("        BIDI: %s\n" % isbidi)
        self.stdout.write("        XWDM: %s\n" % isxwdm)
        self.stdout.write("\n")
        self.stdout.write("        XPON: %s\n" % isxpon)

        self.stdout.write("\n")

        res = {
            "tx": tx,
            "rx": rx,
            "distance": distance,
            "isbidi": isbidi,
            "isxwdm": isxwdm,
            "isxpon": isxpon,
        }

        return res

    def handle(self, apply_mongo, backup_dir, output_dir):
        if output_dir and not os.path.isdir(output_dir) and os.access(output_dir, os.W_OK):
            self.stdout.write("Output dir not exists or not writeable '%s'" % output_dir)
            return

        if backup_dir and not os.path.isdir(backup_dir) and os.access(backup_dir, os.W_OK):
            self.stdout.write("Backup dir not exists or not writeable '%s'" % backup_dir)
            return

        connect()

        items = self.load_collections_from_files()
                    

        for i in items:
            o = items[i].data
            fp = items[i].path
            description = o.get("description", "").strip()

            description = description.lower()
            description = description.replace("(", "")
            description = description.replace(")", "")
            description = description.replace(",", "")
            self.stdout.write("%s\n" % o)
            self.stdout.write("    %s\n" % description)

            res = self.parse_description(description)

            if res["tx"]:
                o["data"] += [{
                    "interface": "optical",
                    "attr": "tx_wavelength",
                    "value": res["tx"]
                }]

            if res["rx"]:
                o["data"] += [{
                    "interface": "optical",
                    "attr": "rx_wavelength",
                    "value": res["rx"]
                }]
                
            if res["distance"]:
                o["data"] += [{
                    "interface": "optical",
                    "attr": "distance_max",
                    "value": res["distance"]
                }]

            o["data"] += [{
                "interface": "optical",
                "attr": "bidi",
                "value": res["isbidi"]
            }]
            o["data"] += [{
                "interface": "optical",
                "attr": "xwdm",
                "value": res["isxwdm"]
            }]

            if output_dir:
                self.save_json(output_dir, fp, o)
            # self.stdout.write("%s\n" % o.to_json())
            continue

                    

        return

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

            isxwdm = False
            for p in self.xwdm_patterns:
                match = p.search(description)
                if match:
                    isxwdm = True
                    break

            isxpon = False
            for p in self.xpon_patterns:
                match = p.search(description)
                if match:
                    isxpon = True
                    break

            tx = 0
            rx = 0
            for p in self.wav_patterns:
                match = p.search(description)
                if match:
                    if not rx and "rx" in match.groupdict():
                        rx = int(match.group("rx"))
                        if tx:
                            break
                    if not tx and "tx" in match.groupdict():
                        tx = int(match.group("tx"))
                        if rx:
                            break
                    if "txrx" in match.groupdict():
                        tx = int(match.group("txrx"))
                        rx = int(match.group("txrx"))
                        break

            # if tx and rx and tx != rx:
            #     isbidi = True

            distance = 0
            for p in self.dist_patterns:
                match = p.search(description)
                if match:
                    if "km" in match.groupdict():
                        distance = int(match.group("km")) * 1000
                        break
                    if "m" in match.groupdict():
                        distance = int(match.group("m"))
                        break

            if not (rx and tx) and isxpon:
                tx = 1490
                rx = 1310

            if distance:
                self.stdout.write("        Distance: %sm\n" % distance)
            if rx:
                self.stdout.write("        RX: %s\n" % rx)
            if tx:
                self.stdout.write("        TX: %s\n" % tx)
            self.stdout.write("        BIDI: %s\n" % isbidi)
            self.stdout.write("        XWDM: %s\n" % isxwdm)
            self.stdout.write("\n")
            self.stdout.write("        XPON: %s\n" % isxpon)

            self.stdout.write("\n")

            if tx:
                o.data += [ModelAttr(interface="optical", attr="tx_wavelength", value=tx)]

            if rx:
                o.data += [ModelAttr(interface="optical", attr="rx_wavelength", value=rx)]

            if distance:
                o.data += [ModelAttr(interface="optical", attr="distance_max", value=distance)]
            
            o.data += [ModelAttr(interface="optical", attr="bidi", value=isbidi)]
            o.data += [ModelAttr(interface="optical", attr="xwdm", value=isxwdm)]

            if output_dir:
                self.save_json(output_dir, o)
            # self.stdout.write("%s\n" % o.to_json())
            continue

        return

class ServiceStub(object):
    class ServiceConfig(object):
        def __init__(self, pool, tos=None):
            self.pool = pool
            self.tos = tos

    def __init__(self, pool):
        self.config = self.ServiceConfig(pool=pool)


if __name__ == "__main__":
    Command().run()
