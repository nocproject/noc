# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Clone remote daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from optparse import make_option
import os
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.lib.updateclient import UpdateClient
from noc.lib.fileutils import copy_file
import ConfigParser


class Command(BaseCommand):
    help = "Clone remote daemon"

    option_list = BaseCommand.option_list + (
        make_option(
            "-l", "--list",
            action="store_const", dest="cmd", const="list",
            help="List manifests"
        ),
        make_option(
            "-m", "--manifest",
            action="store_const", dest="cmd", const="manifest",
            help="display manifest"
        ),
        make_option(
            "-o", "--out", action="store", dest="out",
            help="Output directory"),
    )

    def handle(self, *args, **options):
        cmd = options.get("cmd")
        if not cmd:
            cmd = "clone"
        if cmd:
            return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_list(self, *args, **options):
        names = set()
        for f in os.listdir("etc/manifests/"):
            if f.endswith(".conf"):
                names.add(f[:-5])
            elif f.endswith(".defaults"):
                names.add(f[:-9])
        print "\n".join(sorted(names))

    def handle_manifest(self, *args, **options):
        for name in args:
            uc = UpdateClient("", [name])
            for path in uc.manifest:
                print "%s %s" % (uc.manifest[path], path)

    def handle_clone(self, *args, **options):
        name = args[0]
        out = options.get("out")
        if not out:
            raise CommandError("No output directory")
        if not os.path.isdir(out):
            raise CommandError("%s is not a directory" % out)
        dest = os.path.join(out, "noc")
        if os.path.exists(dest):
            raise CommandError("%s is already exists" % dest)
        # Clone required files
        uc = UpdateClient("", ["launcher", name])
        for f in uc.manifest:
            t = os.path.join(dest, f)
            print "%s -> %s" % (f, t)
            copy_file(f, t)
        # Fix configs
        # noc-launcher.conf
        dc = ConfigParser.SafeConfigParser()
        dc.read("etc/noc-launcher.defaults")
        cp = ConfigParser.SafeConfigParser()
        cp.add_section("update")
        cp.set("update", "url", "http://127.0.0.1:8000/")
        cp.set("update", "enabled", "true")
        cp.set("update", "name", "launcher")
        for s in dc.sections():
            if s.startswith("noc-"):
                cp.add_section(s)
                cp.set(s, "enabled", "false")
        with open(os.path.join(dest, "etc/noc-launcher.conf"), "w") as f:
            cp.write(f)
        # Mark scripts as executable
        if os.path.isdir("scripts"):
            ds = os.path.join(dest, "scripts")
            for f in os.listdir(ds):
                if f.endswith(".py") or "." not in f:
                    p = os.path.join(ds, f)
                    print "CHMOD 0755 %s" % p
                    os.chmod(p, 0755)
        print "Cloning complete"
        print "WARNING:"
        print "Do not forget to set daemons' update configuration"
        print "in [update] section"
        print "and enable appropriative daemons in noc-launcher.conf"
