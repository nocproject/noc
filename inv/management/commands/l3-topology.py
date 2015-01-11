# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## L3 topology
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import tempfile
import subprocess
from optparse import make_option
from collections import namedtuple, defaultdict
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.ip.models.vrf import VRF
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.forwardinginstance import ForwardingInstance
from noc.inv.models.subinterface import SubInterface
from noc.lib.ip import IP
from noc.lib.validators import is_rd


class Command(BaseCommand):
    help = "Show Links"
    option_list = BaseCommand.option_list + (
        make_option("--afi", dest="afi",
                    action="store", default="4",
                    help="AFI (ipv4/ipv6)"),
        make_option("--vrf", dest="vrf", action="store",
                    help="VRF Name/RD"),
        make_option("-o", "--out", dest="output", action="store",
                    help="Save output to file"),
        make_option("--core", dest="core", action="store_true",
                    help="Reduce to network core")
    )

    SI = namedtuple("SI", ["object", "interface", "fi", "ip", "prefix"])
    IPv4 = "4"
    IPv6 = "6"

    GV_FORMAT = {
        ".pdf": "pdf"
    }

    def handle(self, *args, **options):
        # Check AFI
        afi = options["afi"].lower()
        if afi.startswith("ipv"):
            afi = afi[3:]
        elif afi.startswith("ip"):
            afi = afi[2:]
        if afi not in ("4", "6"):
            raise CommandError("Invalid AFI: Must be one of 4, 6")
        # Check graphviz options
        ext = None
        if options["output"]:
            ext = os.path.splitext(options["output"])[-1]
            if ext in self.GV_FORMAT:
                # @todo: Check graphvis
                pass
            elif ext not in ".dot":
                raise CommandError("Unknown output format")
        # Check VRF
        rd = "0:0"
        if options["vrf"]:
            try:
                vrf = VRF.objects.get(name=options["vrf"])
                rd = vrf.rd
            except VRF.DoesNotExist:
                if is_rd(options["vrf"]):
                    rd = options["vrf"]
                else:
                    raise CommandError("Invalid VRF: %s" % options["vrf"])
        self.mo_cache = {}
        self.fi_cache = {}
        self.rd_cache = {}
        self.p_power = defaultdict(int)
        out = ["graph {"]
        out += ["    node [fontsize=12];"]
        out += ["    edge [fontsize=8];"]
        out += ["    overlap=scale;"]
        # out += ["    splines=true;"]
        objects = set()
        prefixes = set()
        interfaces = list(self.get_interfaces(afi, rd))
        if options["core"]:
            interfaces = [si for si in interfaces if self.p_power[si.prefix] > 1]
        for si in interfaces:
            o_id = "o_%s" % si.object
            p_id = "p_%s" % si.prefix.replace(".", "_").replace(":", "__").replace("/", "___")
            if si.object not in objects:
                objects.add(si.object)
                o = self.get_object(si.object)
                if not o:
                    continue
                out += ["    %s [shape=box;style=filled;label=\"%s\"];" % (o_id, o.name)]
            if si.prefix not in prefixes:
                prefixes.add(si.prefix)
                out += ["    %s [shape=ellipse;label=\"%s\"];" % (p_id, si.prefix)]
            out += ["    %s -- %s [label=\"%s\"];" % (o_id, p_id, si.interface)]
        out += ["}"]
        data = "\n".join(out)
        if ext is None:
            print data
        elif ext == ".dot":
            with open(options["output"], "w") as f:
                f.write(data)
        else:
            # Pass to grapviz
            with tempfile.NamedTemporaryFile(suffix=".dot") as f:
                f.write(data)
                f.flush()
                subprocess.check_call([
                    "neato",
                    "-T%s" % self.GV_FORMAT[ext],
                    "-o%s" % options["output"],
                    f.name
                ])

    def get_interfaces(self, afi, rd, selector=None):
        """
        Returns a list of SI
        """
        def check_ipv4(a):
            if a.startswith("127.") or a.startswith("169.254"):
                return False
            else:
                return True

        def check_ipv6(a):
            if a == "::1":
                return False
            else:
                return True

        si_fields = {"_id": 0, "name": 1, "forwarding_instance": 1,
                     "managed_object": 1}
        if afi == self.IPv4:
            check = check_ipv4
            get_addresses = lambda x: x.get("ipv4_addresses", [])
            AFI = "IPv4"
            si_fields["ipv4_addresses"] = 1
        elif afi == self.IPv6:
            check = check_ipv6
            get_addresses = lambda x: x.get("ipv6_addresses", [])
            AFI = "IPv6"
            si_fields["ipv6_addresses"] = 1
        else:
            raise NotImplementedError()
        for si in SubInterface._get_collection().find({"enabled_afi": AFI}, si_fields):
            if rd != self.get_rd(si["managed_object"], si.get("forwarding_instance")):
                continue
            seen = set()
            for a in [a for a in get_addresses(si) if check(a)]:
                prefix = str(IP.prefix(a).first)
                if prefix in seen:
                    continue
                seen.add(prefix)
                self.p_power[prefix] += 1
                yield self.SI(si["managed_object"], si["name"],
                              si.get("forwarding_instance"), a,
                              prefix)

    def get_object(self, o):
        """
        Returns ManagedObject instance
        """
        mo = self.mo_cache.get(o)
        if not mo:
            try:
                mo = ManagedObject.objects.get(id=o)
            except ManagedObject.DoesNotExist:
                mo = None
            self.mo_cache[o] = mo
        return mo

    def get_rd(self, object, fi):
        rd = self.rd_cache.get((object, fi))
        if not rd:
            if fi:
                f = ForwardingInstance.objects.filter(id=fi).first()
                if f:
                    rd = f.rd
                else:
                    rd = None  # Missed data
            else:
                o = self.get_object(object)
                if o:
                    if o.vrf:
                        rd = o.vrf.rd
                    else:
                        rd = "0:0"
                else:
                    rd = None  # Missed data
            self.rd_cache[object, fi] = rd
        return rd
