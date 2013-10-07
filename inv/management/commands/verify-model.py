# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Link management CLI interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from optparse import OptionParser, make_option
from collections import defaultdict
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.inv.models.objectmodel import ObjectModel, ModelConnectionsCache


class Command(BaseCommand):
    help = "Verify models"

    def handle(self, *args, **options):
        CHECK_MAP = {
            "Electrical | RJ45": self.check_ct_rj45,
            "Electrical | Power | IEC 60320 C14": self.check_ct_c14,
            "Transceiver | SFP": self.check_ct_sfp
        }
        for m in ObjectModel.objects.all():
            self.errors = []
            for c in m.connections:
                self.common_check(c)
                check = CHECK_MAP.get(c.type.name)
                if check:
                    check(c)
            if self.errors:
                print "%s errors:" % m.name
                for e in self.errors:
                    print "    %s" % e

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

    def check_ct_rj45(self, c):
        if c.direction != "s":
            self.e(c, "RJ45 must have direction 's' (has '%s')" % c.direction)
        if not c.protocols:
            self.e(c, "RJ45 must have at least one protocol")

    def check_ct_c14(self, c):
        if c.direction != "s":
            self.e(c, "C14 must have direction 's' (has '%s')" % c.direction)
        self.check_protocols(c, [
            ">220VAC", "<220VAC", ">110VAC", "<110VAC"
        ])

    def check_ct_sfp(self, c):
        self.check_protocols(c, [
            "TransEth100M", "TransEth1G", "TransEth10G"
        ])
