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
import sys
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.lib.collection import Collection, DereferenceError
from noc.main.models.doccategory import DocCategory
from noc.gis.models.layer import Layer
from noc.inv.models.technology import Technology
from noc.inv.models.vendor import Vendor
from noc.inv.models.modelinterface import ModelInterface
from noc.inv.models.connectiontype import ConnectionType
from noc.inv.models.connectionrule import ConnectionRule
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.capability import Capability
from noc.sa.models.action import Action
from noc.sa.models.actioncommands import ActionCommands
from noc.cm.models.errortype import ErrorType
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
from noc.pm.models.metrictype import MetricType
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
        ("inv.technologies", Technology),
        ("inv.vendors", Vendor),
        ("inv.modelinterfaces", ModelInterface),
        ("inv.connectiontypes", ConnectionType),
        ("inv.connectionrules", ConnectionRule),
        ("inv.objectmodels", ObjectModel),
        ("inv.capabilities", Capability),
        #
        ("sa.actions", Action),
        ("sa.actioncommands", ActionCommands),
        # Configuration management
        ("cm.errortypes", ErrorType),
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
        ("fm.cloneclassificationrules", CloneClassificationRule),
        # Performance Management
        ("pm.metrictypes", MetricType)
    ]

    cdict = dict(collections)

    def log(self, msg):
        if not self.verbose:
            return
        print msg

    def not_found(self, name):
        msg = "Collection not found: %s" % name
        msg = "%s\nAvailable collections:" % msg
        for n, d in self.collections:
            msg = "%s\n  %s" % (msg, n)
        return msg

    def handle(self, *args, **kwargs):
        try:
            self._handle(*args, **kwargs)
        except CommandError:
            raise
        except:
            error_report()
            sys.exit(1)

    def _handle(self, *args, **options):
        self.verbose = bool(options.get("verbosity"))
        if options["cmd"] == "sync":
            return self.handle_sync()
        elif options["cmd"] == "upgrade":
            return self.handle_upgrade(args)
        elif options["cmd"] == "install":
            # if len(args) < 2:
            #     parts = args[0].split(os.path.sep)
            #     if (len(parts) < 2 or parts[1] != "collections"):
            #         raise CommandError("Usage: <collection> <file1> .. <fileN>")
            #     # Generate collection name from path
            #     name = "%s.%s" % (parts[0], parts[2])
            #     args = [name] + list(args)
            return self.handle_install(args)
            # return self.handle_install(args[0], args[1:])
        elif options["cmd"] == "remove":
            return self.handle_remove(args[0])
        elif options["cmd"] == "check":
            return self.handle_check()
        elif options["cmd"] == "status":
            return self.handle_status(args[1:])

    def fix_categories(self):
        pass

    def get_collection(self, name):
        d = self.cdict.get(name)
        if d:
            return d
        else:
            raise CommandError(self.not_found(name))

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
        except DereferenceError, why:
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

    def handle_install(self, files):
        def iter_files(names):
            for f in names:
                if os.path.isdir(f):
                    for dirpath, dirnames, filenames in os.walk(f):
                        for ff in filenames:
                            if ff.endswith(".json"):
                                yield os.path.join(dirpath, ff)
                else:
                    yield f

        dcs = {}  # name -> collection
        files = list(files)
        if files[0] in self.cdict:
            # Get collection name hints
            current_name = files.pop(0)
        else:
            # Inplace update
            parts = files[0].split(os.path.sep)
            if (len(parts) > 3 and
                    parts[1] == "collections" and
                    "%s.%s" % (parts[0], parts[2]) in self.cdict):
                current_name = "%s.%s" % (parts[0], parts[2])
            else:
                current_name = None

        self.log("Installing files")
        for f in iter_files(files):
            self.log("    ... read %s" % f)
            fd = read_file(f)
            if not fd:
                raise CommandError("Cannot read file: %s" % f)
            try:
                data = json_decode(fd)
            except ValueError:
                raise CommandError("Unable to parse JSON file: %s" % f)
            if "$collection" in data:
                current_name = data["$collection"]
            if not current_name:
                raise CommandError("Cannot detect collection for file: %s" % f)
            if current_name in dcs:
                dc = dcs[current_name]
            else:
                d = self.get_collection(current_name)
                self.log("    ... open collection %s" % current_name)
                dc = Collection(current_name, d)
                dc.load()
                dcs[current_name] = dc
            if "uuid" in data:
                ci = dc.get_item(data["uuid"])
                if ci and dc.get_hash(fd) == ci.hash:
                    self.log("        ... not changed. Skipping")
                    continue  # Not changed
            dc.install_item(data, load=True)
        # Save all modified manifests
        for n, dc in dcs.iteritems():
            self.log("    ... saving manifest.csv for %s" % n)
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
