# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Collections management
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from optparse import make_option
import os
import stat
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.lib.collection import Collection
from noc.main.models.doccategory import DocCategory
from noc.gis.models.layer import Layer
from noc.inv.models.vendor import Vendor
from noc.inv.models.modelinterface import ModelInterface
from noc.inv.models.connectiontype import ConnectionType
from noc.inv.models.connectionrule import ConnectionRule
from noc.inv.models.objectmodel import ObjectModel
from noc.fm.models.oidalias import OIDAlias
from noc.fm.models.syntaxalias import SyntaxAlias
from noc.fm.models.mibalias import MIBAlias
from noc.fm.models.mibpreference import MIBPreference
from noc.fm.models.enumeration import Enumeration
from noc.fm.models.alarmseverity import AlarmSeverity
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.eventclass import EventClass
from noc.fm.models.eventclassificationrule import EventClassificationRule
from noc.fm.models.cloneclassificationrule import CloneClassificationRule
from noc.lib.serialize import json_decode
from noc.lib.fileutils import read_file
from noc.lib.debug import error_report


class Command(BaseCommand):
    """
    Manage Jobs
    """
    help = "Manage Full-Text Search index"
    option_list=BaseCommand.option_list+(
        make_option(
            "--sync", "-s",
            action="store_const",
            dest="cmd",
            const="sync",
            help="Synchronize collections"
        ),
        make_option(
            "--upgrade", "-u",
            action="store_const",
            dest="cmd",
            const="upgrade",
            help="Upgrade collection to a new model"
        ),
        make_option(
            "--install", "-i",
            action="store_const",
            dest="cmd",
            const="install",
            help="Install file to collection"
        ),
        make_option(
            "--remove", "-r",
            action="store_const",
            dest="cmd",
            const="remove",
            help="Remove file from collection"
        ),
        make_option(
            "--check", "-c",
            action="store_const",
            dest="cmd",
            const="check",
            help="Check collections"
        ),
        make_option(
            "--status", "-S",
            action="store_const",
            dest="cmd",
            const="status",
            help="Show status"
        )
    )

    collections = [
        # Gis
        ("gis.layers", Layer),
        # Inventory
        ("inv.vendors", Vendor),
        ("inv.modelinterfaces", ModelInterface),
        ("inv.connectiontypes", ConnectionType),
        ("inv.connectionrules", ConnectionRule),
        ("inv.objectmodels", ObjectModel),
        # Fault Management
        ("fm.oidaliases", OIDAlias),
        ("fm.syntaxaliases", SyntaxAlias),
        ("fm.mibaliases", MIBAlias),
        ("fm.mibpreferences", MIBPreference),
        ("fm.enumerations", Enumeration),
        ("fm.alarmseverities", AlarmSeverity),
        ("fm.alarmclasses", AlarmClass),
        ("fm.eventclasses", EventClass),
        ("fm.eventclassificationrules", EventClassificationRule),
        ("fm.cloneclassificationrules", CloneClassificationRule)
    ]

    def log(self, msg):
        if not self.verbose:
            return
        print msg

    def handle(self, *args, **kwargs):
        try:
            self._handle(*args, **kwargs)
        except CommandError:
            raise
        except:
            error_report()

    def _handle(self, *args, **options):
        self.verbose = bool(options.get("verbosity"))
        if options["cmd"] == "sync":
            return self.handle_sync()
        elif options["cmd"] == "upgrade":
            return self.handle_upgrade(args)
        elif options["cmd"] == "install":
            if len(args) < 2:
                parts = args[0].split(os.path.sep)
                if parts[1] != "collections":
                    raise CommandError("Usage: <collection> <file1> .. <fileN>")
                # Generate collection name from path
                name = "%s.%s" % (parts[0], parts[2])
                args = [name] + list(args)
            return self.handle_install(args[0], args[1:])
        elif options["cmd"] == "remove":
            return self.handle_remove(args[0])
        elif options["cmd"] == "check":
            return self.handle_check()
        elif options["cmd"] == "status":
            return self.handle_status(args[1:])

    def fix_categories(self):
        pass

    def get_collection(self, name):
        for n, d in self.collections:
            if n == name:
                return d
        raise CommandError("Collection not found: %s" % name)

    def handle_sync(self):
        DocCategory.fix_all()
        try:
            for name, doc in self.collections:
                lc = Collection(name, doc, local=True)
                lc.load()
                dc = Collection(name, doc)
                dc.load()
                lc.apply(dc)
        except ValueError, why:
            raise CommandError(why)

    def handle_upgrade(self, collections):
        for c in collections:
            self.log("Upgrading %s" % c)
            d = self.get_collection(c)
            dc = Collection(c, d)
            cr = "%s/collections/%s" % (dc.module, dc.name)
            if os.path.exists(os.path.join(cr, "manifest.csv")):
                raise CommandError("Collection %s is already upgraded" % c)
            fl = []
            for root, dirs, files in os.walk(cr):
                for f in files:
                    if f.endswith(".json"):
                        fl += [os.path.join(root, f)]
            for p in fl:
                s = os.stat(p)
                data = json_decode(read_file(p))
                if isinstance(data, list):
                    for o in data:
                        if "__aliases" in o:
                            del o["__aliases"]
                        dc.install_item(o)
                elif isinstance(data, dict):
                    if "__aliases" in data:
                        del data["__aliases"]
                    dc.install_item(data)
                if os.stat(p)[stat.ST_MTIME] == s[stat.ST_MTIME]:
                    # Remove stale file
                    self.log("    ... removing %s" % p)
                    os.unlink(p)
            self.log("    ... saving manifest.csv")
            dc.save()
        self.log("   ... done")

    def handle_install(self, name, files):
        self.log("Installing files")
        d = self.get_collection(name)
        dc = Collection(name, d)
        dc.load()
        for f in files:
            try:
                data = json_decode(read_file(f))
            except ValueError:
                raise CommandError("Unable to parse JSON file: %s" % f)
            dc.install_item(data, load=True)
        self.log("    ... saving manifest.csv")
        dc.save()

    def handle_remove(self, name):
        raise CommandError("Not implemented yet")

    def handle_check(self):
        try:
            for name, doc in self.collections:
                dc = Collection(name, doc)
                dc.load()
                for mi in dc.items.itervalues():
                    r = dc.check_item(mi)
                    if r:
                        print mi.name
                        for x in r:
                            print "    %s" % x
        except ValueError, why:
            raise CommandError(why)

    def handle_status(self, collections=None):
        if not collections:
            collections = [c[0] for c in self.collections]
        for c in collections:
            d = self.get_collection(c)
            dc = Collection(c, d)
            dc.load()
            print "*", c
            for status, ci in dc.get_status():
                print status, ci
