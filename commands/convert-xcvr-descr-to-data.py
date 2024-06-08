# ----------------------------------------------------------------------
# ./noc convert-xcvr-descr-to-data
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
import os
import errno

# Third-party modules

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.inv.models.objectmodel import ObjectModel, ModelAttr

from noc.core.prettyjson import to_json

from noc.core.collection.base import Collection
from noc.models import get_model


class Dict2Class(object):
    def __init__(self, d: dict):
        for k, v in d.items():
            setattr(self, k, v)


class Command(BaseCommand):
    wav_patterns = [
        re.compile(r"(?:\s|^)(?P<rx>\d+)\s+rx\s+(?P<tx>\d+)\s+tx(?:\s|$)"),
        re.compile(r"(?:\s|^)(?P<tx>\d+)\s+tx\s+(?P<rx>\d+)\s+rx(?:\s|$)"),
        re.compile(r"(?:\s|^)rx (?P<rx>\d+) tx (?P<tx>\d+)(?:\s|$)"),
        re.compile(r"(?:\s|^)tx/rx: (?P<tx>\d+)/(?P<rx>\d+)nm(?:\s|$)"),
        re.compile(r"(?:\s|^)rx-(?P<rx>\d+)/tx-(?P<tx>\d+)(?:\s|$)"),
        re.compile(r"(?:\s|^)tx-(?P<tx>\d+)/rx-(?P<rx>\d+)(?:\s|$)"),
        re.compile(r"(?:\s|^)rx(?P<rx>\d+)/tx(?P<tx>\d+)(?:\s|$)"),
        re.compile(r"(?:\s|^)tx(?P<tx>\d+)(nm)?/rx(?P<rx>\d+)(nm)?(?:\s|$)"),
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
        re.compile(r"(?::|;|\s|^)mmf/smf.*/(?P<km>\d+)km(?::|;|\s|$)"),
    ]

    connector_patterns = [
        re.compile(r"(?:\s|^)(?P<connector>lc)(?:\s|$)"),
        re.compile(r"(?:\s|^)(?P<connector>sc)(?:\s|$)"),
    ]

    transceiver_patterns = [
        re.compile(
            r"(?:\s|^)(10gbase-|sfp\+\s+|10g\s+|xfp\s+|10g\s+base-)(?P<ttype10g>cr|sr|srl|lr|lrm|cx4|lx4|er|zr|t)(?:/|\s|$)"
        ),
        re.compile(
            r"(?:\s|^)(1000base-*|sfp\s+|1g\s+gbic\s+)(?P<ttype1g>bx|lx|lh|ex|sx|zx)\S*(?:\s|$)"
        ),
        re.compile(r"(?:\s|^)(1000base-*|sfp\s+|1g\s+gbic\s+)(?P<ttype1g>t|tx)(?:\s|$)"),
        re.compile(r"(?:\s|^)(?P<ttype1g>lh/lx)\s+transceiver(?:\s|$)"),
    ]

    bidi_patterns = [
        re.compile(r"(?:\s|^)sfp wdm(?:\s|$)"),
        re.compile(r"(?:\s|^)sfp\+ wdm(?:\s|$)"),
        re.compile(r"(?:\s|^)wdm-1g\S+(?:\s|$)"),
        re.compile(r"(?:\s|^)bi-directional(?:\s|$)"),
        re.compile(r"(?:\s|^)bidirectional(?:\s|$)"),
        re.compile(r"(?:\s|^)bidi(?:\s|$)"),
        re.compile(r"(?:\s|^)wdm\S*(?:\s|$)"),
    ]

    xwdm_patterns = [
        re.compile(r"(?:\s|^)cwdm(?:\s|$)"),
    ]

    xpon_patterns = [
        re.compile(r"(?:\s|^)gpon(?:\s|$)"),
        re.compile(r"(?:\s|^)gepon(?:\s|$)"),
        re.compile(r"(?:\s|^)epon(?:\s|$)"),
        re.compile(r"(?:\s|^)epon(?:\S|$)"),
        re.compile(r"(?:\s|^)xpon(?:\s|$)"),
    ]

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--mongo",
            action="store_true",
            default=False,
            dest="mongo",
            help="Use MongoDB as collection source.",
        )
        parser.add_argument(
            "--apply",
            action="store_true",
            default=False,
            dest="apply_mongo",
            help="Store changes to mongo. Make effect only with --mongo.",
        )
        parser.add_argument(
            "--backup-dir",
            dest="backup_dir",
            help="Save collections backup to specified directory before apply.",
        )
        parser.add_argument(
            "--output-dir",
            dest="output_dir",
            help="Save changed collections to specified directory.",
        )

    def makedirs(self, path_: str) -> None:
        """
        Trying to create directories in path_
        """
        try:
            os.makedirs(path_)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def gen_filename(self, output_dir: str, o: ObjectModel) -> str:
        """
        Generate file name from "output_dir" and object name.

        Example:
        output_dir: "/opt/test"
        o.name: "Avaya | Transceiver | 10G | SFP+"

        res: "/opt/test/Avaya/Transceiver/10G/SFP+.json"
        """
        name_parts = o.name.split("|")
        name_parts = [s.strip().replace(" ", "_") for s in name_parts]
        name_parts[-1] += ".json"

        file_name = os.path.join(output_dir, *name_parts)

        return file_name

    def save_obj_json(self, o_dir: str, o: ObjectModel) -> None:
        """
        Save "o" object as JSON to "o_dir"
        """
        fname = self.gen_filename(o_dir, o)
        dir_name = os.path.dirname(fname)

        self.makedirs(dir_name)

        with open(fname, "w") as f:
            f.write(o.to_json())

        return

    def save_json(self, o_dir: str, path_: str, o: dict) -> None:
        """
        Save "o" dictionary as JSON to "o_dir"
        """
        fname = os.path.join(o_dir, *path_.split("/")[2:])
        dir_name = os.path.dirname(fname)

        self.makedirs(dir_name)

        with open(fname, "w") as f:
            f.write(
                to_json(
                    o,
                    order=[
                        "name",
                        "$collection",
                        "uuid",
                        "vendor__code",
                        "description",
                        "connection_rule__name",
                        "cr_context",
                        "plugins",
                        "labels",
                        "connections",
                        "data",
                    ],
                )
            )

        return

    def load_collections_from_files(self) -> dict:
        """
        Returns dictionary of collection items
        that have "transceiver" in file path
        """
        items = {}
        cm = get_model("inv.ObjectModel")
        cn = cm._meta["json_collection"]
        c = Collection(cn)

        cdata = c.get_items()
        for x in cdata:
            if "transceiver" in cdata[x].data["name"].lower():
                items[x] = cdata[x]

        return items

    def parse_description(self, description):
        """
        Parse description string by applying patterns
        then return object with data
        """

        ttype1g_bidi = [
            "bx",
        ]

        ttype1g_distance_map = {
            "t": 100,
            "tx": 100,
            "sx": 300,
            "bx": 5000,
            "lx": 5000,
            "lh": 10000,
            "lh/lx": 20000,
            "ex": 40000,
            "zx": 80000,
        }

        ttype10g_distance_map = {
            "t": 100,
            "tx": 100,
            "cx4": 15,
            "sr": 300,
            "lr": 10000,
            "lrm": 10000,
            "lx4": 10000,
            "er": 40000,
            "zr": 80000,
        }

        connector = ""
        for p in self.connector_patterns:
            match = p.search(description)
            if match:
                if "connector" in match.groupdict():
                    connector = match.group("connector")

        ttype1g = ""
        ttype10g = ""
        for p in self.transceiver_patterns:
            match = p.search(description)
            if match:
                if "ttype10g" in match.groupdict():
                    ttype10g = match.group("ttype10g")

                if "ttype1g" in match.groupdict():
                    ttype1g = match.group("ttype1g")

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

        # XPON is always bidirectional
        if not isbidi:
            isbidi = isxpon

        # Check transceiver type for bidi
        if not isbidi:
            if ttype1g:
                isbidi = ttype1g in ttype1g_bidi

        # GPON and GEPON(EPON) have tx=1490 and rx=1310
        if not (rx and tx) and isxpon:
            tx = 1490
            rx = 1310

        # Check transceiver type for distance
        if not distance:
            if ttype1g:
                distance = ttype1g_distance_map.get(ttype1g, 0)
            if ttype10g:
                distance = ttype10g_distance_map.get(ttype10g, 0)

        res = Dict2Class(
            {
                "tx": tx,
                "rx": rx,
                "distance": distance,
                "isbidi": isbidi,
                "isxwdm": isxwdm,
                "isxpon": isxpon,
                "connector": connector,
                "ttype1g": ttype1g,
                "ttype10g": ttype10g,
            }
        )

        return res

    def print_debug(self, rec) -> None:
        if rec.connector:
            self.stdout.write("        CONNECTOR: %s\n" % rec.connector)

        if rec.ttype1g:
            self.stdout.write("        TTYPE1G: %s\n" % rec.ttype1g)

        if rec.ttype10g:
            self.stdout.write("        TTYPE10G: %s\n" % rec.ttype10g)

        if rec.distance:
            self.stdout.write("        Distance: %sm\n" % rec.distance)
        if rec.rx:
            self.stdout.write("        RX: %s\n" % rec.rx)
        if rec.tx:
            self.stdout.write("        TX: %s\n" % rec.tx)
        self.stdout.write("        BIDI: %s\n" % rec.isbidi)
        self.stdout.write("        XWDM: %s\n" % rec.isxwdm)
        self.stdout.write("\n")
        self.stdout.write("        XPON: %s\n" % rec.isxpon)

        self.stdout.write("\n")

    def clear_description(self, description: str) -> str:
        description = description.lower()
        description = description.replace("(", "")
        description = description.replace(")", "")
        description = description.replace(",", "")
        return description

    def is_list_contain_attr(self, list_, attr) -> bool:
        for o in list_:
            if o["interface"] == "optical" and o["attr"] == attr:
                return True
        return False

    def handle_files(self) -> None:
        connect()

        items = self.load_collections_from_files()

        for i in items:
            o = items[i].data
            fp = items[i].path
            description = o.get("description", "").strip()
            description = self.clear_description(description)

            res = self.parse_description(description)
            self.stdout.write("%s\n" % o.get("name", ""))
            if self.is_debug:
                self.stdout.write("    %s\n" % description)
                self.print_debug(res)

            if self.__backup_dir:
                self.save_json(self.__backup_dir, fp, o)

            if res.tx and not self.is_list_contain_attr(o["data"], "tx_wavelength"):
                o["data"] += [{"interface": "optical", "attr": "tx_wavelength", "value": res.tx}]

            if res.rx and not self.is_list_contain_attr(o["data"], "rx_wavelength"):
                o["data"] += [{"interface": "optical", "attr": "rx_wavelength", "value": res.rx}]

            if res.distance and not self.is_list_contain_attr(o["data"], "distance_max"):
                o["data"] += [
                    {"interface": "optical", "attr": "distance_max", "value": res.distance}
                ]

            if not self.is_list_contain_attr(o["data"], "bidi"):
                o["data"] += [{"interface": "optical", "attr": "bidi", "value": res.isbidi}]
            if not self.is_list_contain_attr(o["data"], "xwdm"):
                o["data"] += [{"interface": "optical", "attr": "xwdm", "value": res.isxwdm}]

            if self.__output_dir:
                self.save_json(self.__output_dir, fp, o)

    def handle_mongo(self) -> None:
        connect()

        for o in ObjectModel.objects.filter(name={"$regex": ".*Transceiver.*"}):
            description = o.description.strip()
            description = self.clear_description(description)

            res = self.parse_description(description)
            self.stdout.write("%s\n" % o.name)
            if self.is_debug:
                self.stdout.write("    %s\n" % description)
                self.print_debug(res)

            if self.__backup_dir:
                self.save_obj_json(self.__backup_dir, o)

            json_data = o.json_data.get("data")

            if res.tx and not self.is_list_contain_attr(json_data, "tx_wavelength"):
                o.data += [ModelAttr(interface="optical", attr="tx_wavelength", value=res.tx)]

            if res.rx and not self.is_list_contain_attr(json_data, "rx_wavelength"):
                o.data += [ModelAttr(interface="optical", attr="rx_wavelength", value=res.rx)]

            if res.distance and not self.is_list_contain_attr(json_data, "distance_max"):
                o.data += [ModelAttr(interface="optical", attr="distance_max", value=res.distance)]

            if not self.is_list_contain_attr(json_data, "bidi"):
                o.data += [ModelAttr(interface="optical", attr="bidi", value=res.isbidi)]

            if not self.is_list_contain_attr(json_data, "xwdm"):
                o.data += [ModelAttr(interface="optical", attr="xwdm", value=res.isxwdm)]

            if self.__output_dir:
                self.save_obj_json(self.__output_dir, o)

            if self.__apply_mongo:
                o.save()

    def handle(self, mongo, apply_mongo, output_dir, backup_dir):
        self.__mongo = mongo
        self.__apply_mongo = apply_mongo
        self.__output_dir = output_dir
        self.__backup_dir = backup_dir

        if apply_mongo and not mongo:
            self.stdout.write('"--apply" can used only with "--mongo"\n')
            return

        if output_dir and not os.path.isdir(output_dir) and os.access(output_dir, os.W_OK):
            self.stdout.write("Output dir not exists or not writeable '%s'\n" % output_dir)
            return

        if backup_dir and not os.path.isdir(backup_dir) and os.access(backup_dir, os.W_OK):
            self.stdout.write("Backup dir not exists or not writeable '%s'\n" % backup_dir)
            return

        if mongo:
            self.handle_mongo()
        else:
            self.handle_files()


class ServiceStub(object):
    class ServiceConfig(object):
        def __init__(self, pool, tos=None):
            self.pool = pool
            self.tos = tos

    def __init__(self, pool):
        self.config = self.ServiceConfig(pool=pool)


if __name__ == "__main__":
    Command().run()
