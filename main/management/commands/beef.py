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
import pprint
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.lib.test.beeftestcase import BeefTestCase
from noc.lib.fileutils import copy_file


class Command(BaseCommand):
    help = "Beef management utility"

    option_list = BaseCommand.option_list + (
        make_option("-L", "--list-repo",
            action="store_const", dest="cmd", const="list_repo",
            help="List repos"
        ),
        make_option("-p", "--pull",
            action="store_const", dest="cmd", const="pull",
            help="Pull repos"),
        make_option("-r", "--repo", action="store", dest="repo",
            help="Select repo"),
        make_option("-l", "--list", action="store_const", dest="cmd",
            const="list"),
        make_option("-V", "--view", action="store_const", dest="cmd",
            const="view"),
        make_option("-i", "--import", action="store_const", dest="cmd",
            const="import")
    )

    def local_repo_path(self, r):
        return "local/repos/%s/%s/" % (r.type, r.name)

    def iter_repos(self, **options):
        repo = options.get("repo")
        for r in self.repos:
            if repo and r.name != repo:
                continue
            if not r.enabled:
                continue
            yield r

    def iter_repo_files(self, r):
        for prefix, dirnames, filenames in os.walk(self.local_repo_path(r)):
            for f in filenames:
                if f.endswith(".json"):
                    yield os.path.join(prefix, f)

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

    def handle_pull(self, *args, **options):
        for r in self.iter_repos(**options):
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
            print "[%s]" % r.name
            self.hg(rp, "pull", r.repo, "-u")

    def handle_list(self, *args, **options):
        print "Repo,Profile,Script,Vendor,Platform,Version,GUID"
        for r in self.iter_repos(**options):
            for f in  self.iter_repo_files(r):
                tc = BeefTestCase()
                tc.load_beef(f)
                profile, script = tc.script.rsplit(".", 1)
                print "%s,%s,%s,%s,%s,%s,%s" % (
                    r.name, profile, script,
                    tc.vendor, tc.platform, tc.version, tc.guid)

    def show_beef(self, path):
        tc = BeefTestCase()
        tc.load_beef(path)
        print "===[ %s {%s} ]==========" % (tc.script, tc.guid)
        print "Platform: %s %s" % (tc.vendor, tc.platform)
        print "Version : %s" % tc.version
        print "Date    : %s" % tc.date
        if tc.input:
            print "---[ Input ] -----------"
            pprint.pprint(tc.input)
        if tc.result:
            print "---[ Result ] -----------"
            pprint.pprint(tc.result)
        if tc.cli:
            print "---[ CLI ] ----------"
            for cmd in tc.cli:
                print "+--->>>", cmd
                print tc.cli[cmd]
        if tc.snmp_get:
            print "---[SNMP GET]---"
            pprint.pprint(tc.snmp_get)
        if tc.snmp_getnext:
            print "---[SNMP GET]---"
            pprint.pprint(tc.snmp_getnext)

    def handle_view(self, *args, **options):
        for r in self.iter_repos(**options):
            for f in self.iter_repo_files(r):
                d, fn = os.path.split(f)
                guid, _ = os.path.splitext(fn)
                if guid in args:
                    self.show_beef(f)

    def handle_import(self, *args, **options):
        if not options.get("repo"):
            raise CommandError("--repo <repo> is missed")
        repo = list(self.iter_repos(**options))
        if len(repo) != 1:
            raise CommandError("Repo not found")
        repo = repo[0]
        r_path = self.local_repo_path(repo)
        for f in args:
            if not os.path.isfile(f):
                raise CommandError("File not found: %s" % f)
            tc = BeefTestCase()
            tc.load_beef(f)
            if tc.private and not repo.private:
                raise CommandError("%s: Cannot store private beef in the public repo" % f)
            s = tc.script.split(".")
            path = os.path.join(*([r_path] + s + ["%s.json" % tc.guid]))
            print "Importing %s -> %s" % (f, path)
            copy_file(f, path)
