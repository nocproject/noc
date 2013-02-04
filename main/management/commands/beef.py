# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Beef management
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from optparse import make_option
import ConfigParser
from collections import namedtuple
import os
import subprocess
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.lib.test.beeftestcase import BeefTestCase


class Command(BaseCommand):
    help = "Beef management utility"

    option_list = BaseCommand.option_list + (
        make_option("-L", "--list-repo",
            action="store_const", dest="cmd", const="list_repo",
            help="List repos"
        ),
        make_option("-T", "--test-runner",
            action="store_const", dest="cmd", const="test_runner",
            help="List repos"
        ),
        make_option("-p", "--pull",
            action="store_const", dest="cmd", const="pull",
            help="Pull repos"),
        make_option("-r", "--repo", action="store", dest="repo",
            help="Select repo"),
        make_option("-l", "--list", action="store_const", dest="cmd",
            const="list")
    )

    def local_repo_path(self, r):
        return "local/repos/%s/%s/" % (r.type, r.name)

    def load_config(self):
        config = ConfigParser.SafeConfigParser()
        config.read("etc/beef.defaults")
        config.read("etc/beef.conf")
        Repo = namedtuple(
            "Repo", ["name", "enabled", "type", "private", "repo"])
        self.repos = []
        for s in config.sections():
            self.repos += [
                Repo(
                    name=s,
                    enabled=config.getboolean(s, "enabled"),
                    type=config.get(s, "type"),
                    private=config.getboolean(s, "private"),
                    repo=config.get(s, "repo")
                )
            ]

    def handle(self, *args, **options):
        self.load_config()
        cmd = options.get("cmd")
        if cmd:
            return getattr(self, "handle_%s" % cmd)(*args, **options)

    def hg(self, cwd, *args):
        r = subprocess.call(["hg", "--cwd", cwd] + list(args))
        if r:
            raise CommandError("Failed to call hg --cwd %s %s" % (cwd, args))

    def handle_list_repo(self, *args, **options):
        repo = options.get("repo")
        print "E P T  Name                 Repo"
        for r in self.repos:
            if repo and r.name != repo:
                continue
            print "%s %s %s %-20s %s" % (
                "+" if r.enabled else "-",
                "Y" if r.private else "N",
                r.type, r.name, r.repo)

    def handle_test_runner(self, *args, **options):
        r = [self.local_repo_path(r) for r in self.repos if r.enabled]
        print " ".join("--beef=%s" % x for x in r)

    def handle_pull(self, *args, **options):
        repo = options.get("repo")
        for r in self.repos:
            if repo and r.name != repo:
                continue
            if not r.enabled:
                continue
            # Create repo directory
            rp = self.local_repo_path(r)
            if not os.path.isdir(rp):
                try:
                    os.makedirs(rp)
                except OSError, why:
                    raise CommandError(why)
            # Initialize repo
            if not os.path.isdir(os.path.join(rp, ".hg")):
                self.hg(rp, "init")
            # Pull repo
            self.hg(rp, "pull", r.repo, "-u")

    def handle_list(self, *args, **options):
        repo = options.get("repo")
        print "Repo,Profile,Script,Vendor,Platform,Version,GUID"
        for r in self.repos:
            if repo and r.name != repo:
                continue
            if not r.enabled:
                continue
            for prefix, dirnames, filenames in os.walk(self.local_repo_path(r)):
                for f in filenames:
                    if not f.endswith(".json"):
                        continue
                    tc = BeefTestCase()
                    tc.load_beef(os.path.join(prefix, f))
                    profile, script = tc.script.rsplit(".", 1)
                    print "%s,%s,%s,%s,%s,%s,%s" % (
                        r.name, profile, script,
                        tc.vendor, tc.platform, tc.version, tc.guid)