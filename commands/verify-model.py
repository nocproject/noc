# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Link management CLI interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import argparse
# NOC modules
from noc.core.management.base import BaseCommand
from noc.inv.models.objectmodel import ObjectModel, ModelConnectionsCache


class Command(BaseCommand):
    help = "Verify models"

    def add_arguments(self, parser):
        parser.add_argument("-r", "--rebuild",
                            dest="action",
                            action="store_const", const="rebuild_cache",
                            help="Rebuild connection cache")

    def handle(self, *args, **options):
        if options.get("action") == "rebuild_cache":
            self.stdout.write("Rebuilding connections cache")
            ModelConnectionsCache.rebuild()

        CHECK_MAP = {
            "Electrical | DB9": self.check_ct_db9,
            "Electrical | RJ45": self.check_ct_rj45,
            "Electrical | Power | IEC 60320 C14": self.check_ct_c14,
            "Electrical | SFF-8470": self.check_ct_sff8470,
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
            "Transceiver | XENPAK | Cisco": self.check_ct_xenpak
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
            self.e(c, "Invalid gender '%s' for connection type '%s' (Must me one of '%s')" % (
                c.gender, c.type.name, c.type.genders
            ))

    def check_protocols(self, c, protocols):
        if c.protocols:
            for p in protocols:
                if p in c.protocols:
                    return
        self.e(c, "Must have one of protocols: %s" % ", ".join(protocols))

    def check_direction(self, c, directions):
        if (c.direction) and (c.direction in directions):
            return
        self.e(c, "'%s' must have direction %s (has '%s')" % (
            c.type.name, directions, c.direction
        ))

    def check_ct_db9(self, c):
        self.check_direction(c, ["s"])
        self.check_protocols(c, [
            ">RS232"
        ])

    def check_ct_rj45(self, c):
        self.check_direction(c, ["s"])
        if not c.protocols:
            self.e(c, "RJ45 must have at least one protocol")

    def check_ct_c14(self, c):
        self.check_direction(c, ["s"])
        self.check_protocols(c, [
            ">220VAC", "<220VAC", ">110VAC", "<110VAC"
        ])

    def check_ct_sff8470(self, c):
        self.check_direction(c, ["s"])
        self.check_protocols(c, [
            "10GBASECX4"
        ])

    def check_ct_sfp(self, c):
        self.check_direction(c, ["i", "o"])
        self.check_protocols(c, [
            "TransEth100M", "TransEth1G", "TransEth10G", "TransEth40G"
        ])

    def check_ct_sfp_plus(self, c):
        self.check_direction(c, ["i", "o"])
        self.check_protocols(c, [
            "TransEth1G", "TransEth10G"
        ])

    def check_ct_qsfp_plus(self, c):
        self.check_direction(c, ["i", "o"])
        self.check_protocols(c, [
            "TransEth1G", "TransEth10G", "TransEth40G"
        ])

    def check_ct_xfp(self, c):
        self.check_direction(c, ["i", "o"])
        # TODO: Add "TransEth10G" protocol to models
        return
        self.check_protocols(c, [
            "TransEth10G"
        ])

    def check_ct_gbic(self, c):
        self.check_direction(c, ["i", "o"])
        self.check_protocols(c, [
            "TransEth100M", "TransEth1G", "TransEth10G", "TransEth40G"
        ])

    def check_ct_xenpak(self, c):
        self.check_direction(c, ["i", "o"])
        self.check_protocols(c, [
            "TransEth10G"
        ])

if __name__ == "__main__":
    Command().run()
