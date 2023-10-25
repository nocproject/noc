# ---------------------------------------------------------------------
# Link management CLI interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.inv.models.objectmodel import ObjectModel, ModelConnectionsCache
from noc.inv.models.protocol import ProtocolVariant


class Command(BaseCommand):
    help = "Verify models"

    def add_arguments(self, parser):
        parser.add_argument(
            "-r",
            "--rebuild",
            dest="action",
            action="store_const",
            const="rebuild_cache",
            help="Rebuild connection cache",
        )

    def handle(self, *args, **options):
        connect()
        if options.get("action") == "rebuild_cache":
            self.stdout.write("Rebuilding connections cache")
            ModelConnectionsCache.rebuild()

        CHECK_MAP = {
            "Electrical | DB9": self.check_ct_db9,
            "Electrical | RJ45": self.check_ct_rj45,
            "Electrical | Power | IEC 60320 C14": self.check_ct_c14,
            "Electrical | SFF-8470": self.check_ct_sff8470,
            "Optical | LC": self.check_optical_lc,
            "Optical | SC": self.check_optical_lc,  # Same as 'Optical | LC'
            "Transceiver | SFP": self.check_ct_sfp,
            "Transceiver | SFP | Cisco": self.check_ct_sfp,
            "Transceiver | SFP+": self.check_ct_sfp_plus,
            "Transceiver | SFP+ | Cisco": self.check_ct_sfp_plus,
            "Transceiver | SFP+ | Force10": self.check_ct_sfp_plus,
            "Transceiver | SFP+ | Juniper": self.check_ct_sfp_plus,
            "Transceiver | QSFP+": self.check_ct_qsfp_plus,
            "Transceiver | XFP": self.check_ct_xfp,
            "Transceiver | XFP | Cisco": self.check_ct_xfp,
            "Transceiver | GBIC": self.check_ct_gbic,
            "Transceiver | XENPAK | Cisco": self.check_ct_xenpak,
            "Transceiver | X2 | Cisco": self.check_ct_xenpak,  # Same as 'XENPAK | Cisco'
            "Transceiver | CFP": self.check_ct_cfp,
        }
        for m in ObjectModel.objects.all():
            self.errors = []
            if (m.connection_rule is not None) and (not m.cr_context):
                self.errors += ["Missing 'cr_context' field"]
            for c in m.connections:
                self.common_check(c)
                check = CHECK_MAP.get(c.type.name)
                if check:
                    check(c)
            if self.errors:
                self.stdout.write("%s errors:\n" % m.name)
                for e in self.errors:
                    self.stdout.write("    %s\n" % e)

    def e(self, connection, msg):
        self.errors += ["%s: %s" % (connection.name, msg)]

    def common_check(self, c):
        if c.gender not in c.type.genders:
            self.e(
                c,
                "Invalid gender '%s' for connection type '%s' (Must me one of '%s')"
                % (c.gender, c.type.name, c.type.genders),
            )

    def check_protocols(self, c, protocols):
        if c.protocols:
            for p in protocols:
                if ProtocolVariant.get_by_code(p) in c.protocols:
                    return
        self.e(
            c,
            'Has "%s", but must have one of protocols: %s'
            % (", ".join(str(p) for p in c.protocols), ", ".join(str(p) for p in protocols)),
        )

    def check_direction(self, c, directions):
        if (c.direction) and (c.direction in directions):
            return
        self.e(c, "'%s' must have direction %s (has '%s')" % (c.type.name, directions, c.direction))

    def check_ct_db9(self, c):
        self.check_direction(c, ["s"])
        self.check_protocols(c, [">RS232"])

    def check_ct_rj45(self, c):
        self.check_direction(c, ["s"])
        self.check_protocols(
            c,
            [
                "10BASET",
                "100BASETX",
                "1000BASET",  # Cat 5, 5e, 6, 7
                "1000BASETX",  # Cat 6, 7
                "2.5GBASET",
                "5GBASET",
                "10GBASET",
                "G703",
                ">RS232",
                ">RS485",
                ">DryContact",
            ],
        )

    def check_ct_c14(self, c):
        self.check_direction(c, ["s"])
        self.check_protocols(c, [">220VAC", "<220VAC", ">110VAC", "<110VAC"])

    def check_ct_sff8470(self, c):
        self.check_direction(c, ["s"])
        self.check_protocols(c, ["10GBASECX4"])

    def check_optical_lc(self, c):
        self.check_direction(c, ["s"])
        if any("100BASEFX" in s for s in c.protocols):
            self.check_protocols(
                c,
                [
                    ">100BASEFX-1310",
                    "<100BASEFX-1310",
                    ">100BASEFX-1490",
                    "<100BASEFX-1490",
                    ">100BASEFX-1550",
                    "<100BASEFX-1550",
                ],
            )
        elif any("100BASELX10" in s for s in c.protocols):
            self.check_protocols(
                c,
                [
                    ">100BASELX10-1310",
                    "<100BASELX10-1310",
                    ">100BASELX10-1550",
                    "<100BASELX10-1550",
                ],
            )
        elif any("1000BASEZX" in s for s in c.protocols):
            self.check_protocols(
                c,
                [
                    ">1000BASEZX",  # 1270~1620
                    ">1000BASEZX-1350",
                    "<1000BASEZX-1350",
                    ">1000BASEZX-1370",
                    "<1000BASEZX-1370",
                    ">1000BASEZX-1390",
                    "<1000BASEZX-1390",
                    ">1000BASEZX-1410",
                    "<1000BASEZX-1410",
                    ">1000BASEZX-1430",
                    "<1000BASEZX-1430",
                    ">1000BASEZX-1450",
                    "<1000BASEZX-1450",
                    ">1000BASEZX-1470",
                    "<1000BASEZX-1470",
                    ">1000BASEZX-1490",
                    "<1000BASEZX-1490",
                    ">1000BASEZX-1510",
                    "<1000BASEZX-1510",
                    ">1000BASEZX-1530",
                    "<1000BASEZX-1530",
                    ">1000BASEZX-1550",
                    "<1000BASEZX-1550",
                    ">1000BASEZX-1570",
                    "<1000BASEZX-1570",
                    ">1000BASEZX-1590",
                    "<1000BASEZX-1590",
                    ">1000BASEZX-1610",
                    "<1000BASEZX-1610",
                ],
            )
        elif any("10GBASE" in s for s in c.protocols):
            self.check_protocols(
                c,
                [
                    ">10GBASELR-1310",
                    "<10GBASELR-1310",
                    ">10GBASESR-1550",
                    "<10GBASESR-1550",
                    ">10GBASELR-1550",
                    "<10GBASELR-1550",
                    ">10GBASEER-1550",
                    "<10GBASEER-1550",
                    ">10GBASEZR-1550",
                    "<10GBASEZR-1550",
                    ">10GBASESR",
                    "<10GBASESR",
                    ">10GBASESR-850",
                    "<10GBASESR-850",
                ],
            )
        else:
            self.check_protocols(
                c,
                [
                    ">100BASEFX-1310",
                    "<100BASEFX-1310",
                    ">100BASEFX-1490",
                    "<100BASEFX-1490",
                    ">100BASEFX-1550",
                    "<100BASEFX-1550",
                    ">100BASELX10-1310",
                    "<100BASELX10-1310",
                    ">100BASELX10-1550",
                    "<100BASELX10-1550",
                    ">1000BASESX",
                    "<1000BASESX",
                    ">1000BASELX-850",
                    "<1000BASELX-850",
                    ">1000BASELX-1310",
                    "<1000BASELX-1310",
                    ">1000BASELX-1490",
                    "<1000BASELX-1490",
                    ">1000BASELX-1550",
                    "<1000BASELX-1550",
                    ">1000BASEEX-1310",
                    "<1000BASEEX-1310",
                    ">1000BASEZX",  # 1270~1620
                    ">1000BASEZX-1350",
                    "<1000BASEZX-1350",
                    ">1000BASEZX-1370",
                    "<1000BASEZX-1370",
                    ">1000BASEZX-1390",
                    "<1000BASEZX-1390",
                    ">1000BASEZX-1410",
                    "<1000BASEZX-1410",
                    ">1000BASEZX-1430",
                    "<1000BASEZX-1430",
                    ">1000BASEZX-1450",
                    "<1000BASEZX-1450",
                    ">1000BASEZX-1470",
                    "<1000BASEZX-1470",
                    ">1000BASEZX-1490",
                    "<1000BASEZX-1490",
                    ">1000BASEZX-1510",
                    "<1000BASEZX-1510",
                    ">1000BASEZX-1530",
                    "<1000BASEZX-1530",
                    ">1000BASEZX-1550",
                    "<1000BASEZX-1550",
                    ">1000BASEZX-1570",
                    "<1000BASEZX-1570",
                    ">1000BASEZX-1590",
                    "<1000BASEZX-1590",
                    ">1000BASEZX-1610",
                    "<1000BASEZX-1610",
                    ">10GBASESR-850",
                    "<10GBASESR-850",
                    ">10GBASESR-1550",
                    "<10GBASESR-1550",
                    ">10GBASELR-1310",
                    "<10GBASELR-1310",
                    ">10GBASELR-1550",
                    "<10GBASELR-1550",
                    ">10GBASEER-1550",
                    "<10GBASEER-1550",
                    ">10GBASEZR-1550",
                    "<10GBASEZR-1550",
                    ">10GBASESR",
                    "<10GBASESR",
                ],
            )

    def check_ct_sfp(self, c):
        self.check_direction(c, ["i", "o"])
        self.check_protocols(
            c, ["TransEth100M", "TransEth1G", "TransEth10G", "TransEth40G", "GPON"]
        )

    def check_ct_sfp_plus(self, c):
        self.check_direction(c, ["i", "o"])
        self.check_protocols(c, ["TransEth1G", "TransEth10G"])

    def check_ct_qsfp_plus(self, c):
        self.check_direction(c, ["i", "o"])
        self.check_protocols(c, ["TransEth1G", "TransEth10G", "TransEth40G"])

    def check_ct_xfp(self, c):
        self.check_direction(c, ["i", "o"])
        self.check_protocols(c, ["TransEth10G"])

    def check_ct_gbic(self, c):
        self.check_direction(c, ["i", "o"])
        self.check_protocols(c, ["TransEth100M", "TransEth1G", "TransEth10G", "TransEth40G"])

    def check_ct_xenpak(self, c):
        self.check_direction(c, ["i", "o"])
        self.check_protocols(c, ["TransEth10G"])

    def check_ct_cfp(self, c):
        self.check_direction(c, ["i", "o"])
        self.check_protocols(c, ["TransEth40G", "TransEth100G"])


if __name__ == "__main__":
    Command().run()
