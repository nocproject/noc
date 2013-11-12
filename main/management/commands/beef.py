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
from collections import defaultdict
import uuid
import datetime
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.lib.test.beeftestcase import BeefTestCase
from noc.lib.fileutils import copy_file, safe_rewrite
from noc.lib.serialize import json_encode


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
        make_option("--push",
            action="store_const", dest="cmd", const="push",
            help="Push repos"),
        make_option("-r", "--repo", action="store", dest="repo",
            help="Select repo"),
        make_option("-l", "--list", action="store_const", dest="cmd",
            const="list"),
        make_option("-V", "--view", action="store_const", dest="cmd",
            const="view"),
        make_option("-i", "--import", action="store_const", dest="cmd",
            const="import"),
        make_option("--create", action="store_const", dest="cmd",
                    const="create"),
        make_option("--rm", action="store_true", dest="remove"),
        make_option("--clone-version", action="store", dest="clone-version"),
        make_option("-m", "--manifest", action="store_const", dest="cmd",
            const="manifest"),
        make_option("--ensure-private", action="store_const", dest="cmd",
            const="ensure_private"),
        make_option("--cli", action="append", dest="cli"),
        make_option("--result", action="append", dest="result"),
        make_option("--script", action="store", dest="script"),
        make_option("--platform", action="store", dest="platform")
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
        r = subprocess.call(["hg"] + list(args), cwd=cwd)
        if r:
            raise CommandError("Failed to call `cd %s && hg  %s`" % (
                cwd, " ".join(args)))

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

    def handle_push(self, *args, **options):
        # First, pull updates
        print "Pulling ..."
        self.handle_pull(*args, **options)
        # Next, build manifests
        print "Rebuilding manifests ..."
        self.handle_manifest(*args, **options)
        # Commit and push
        print "Pushing"
        for r in self.iter_repos(**options):
            # Create repo directory
            rp = self.local_repo_path(r)
            # Push repo
            print "[%s]" % r.name
            self.hg(rp, "add")
            try:
                self.hg(rp, "commit", "-m", "New beef")
            except CommandError:
                pass
            try:
                self.hg(rp, "push", r.repo)
            except CommandError:
                pass

    def handle_list(self, *args, **options):
        print "Repo,Profile,Script,Vendor,Platform,Version,GUID"
        for r in self.iter_repos(**options):
            for f in self.iter_repo_files(r):
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
        print "Scope   : %s" % "PRIVATE" if tc.private else "PUBLIC"
        if tc.input:
            print "---[ Input ] -----------"
            pprint.pprint(tc.input)
        if tc.result:
            if (isinstance(tc.result, basestring)
                and "START OF TRACEBACK" in tc.result):
                print "---[ Traceback ]---\n%s" % tc.result
            else:
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
        for f in args:
            if os.path.isfile(f):
                self.show_beef(f)
        for r in self.iter_repos(**options):
            for f in self.iter_repo_files(r):
                d, fn = os.path.split(f)
                guid, _ = os.path.splitext(fn)
                if guid in args:
                    self.show_beef(f)

    def handle_import(self, *args, **options):
        if not options.get("repo"):
            raise CommandError("--repo <repo> is missed")
        to_remove = options.get("remove", False)
        repo = list(self.iter_repos(**options))
        if len(repo) != 1:
            raise CommandError("Repo not found")
        repo = repo[0]
        r_path = self.local_repo_path(repo)
        cv = options.get("clone-version")
        vendor = None
        platform = None
        version = None
        if cv:
            tc = BeefTestCase()
            tc.load_beef(cv)
            vendor = tc.vendor
            platform = tc.platform
            version = tc.version
        for f in args:
            if not os.path.isfile(f):
                raise CommandError("File not found: %s" % f)
            tc = BeefTestCase()
            tc.load_beef(f)
            if tc.private and not repo.private:
                raise CommandError("%s: Cannot store private beef in the public repo" % f)
            if cv:
                tc.vendor = vendor
                tc.platform = platform
                tc.version = version
            if not tc.vendor or not tc.platform or not tc.version:
                raise CommandError("%f: No version info" % f)
            s = tc.script.split(".")
            path = os.path.join(*([r_path] + s + ["%s.json" % tc.guid]))
            print "Importing %s -> %s" % (f, path)
            copy_file(f, path, mode=0644)
            if to_remove:
                os.unlink(f)

    def handle_manifest(self, *args, **options):
        for r in self.iter_repos(**options):
            sv = defaultdict(set)
            for f in self.iter_repo_files(r):
                tc = BeefTestCase()
                tc.load_beef(f)
                sv[tc.script].add(("%s %s" % (tc.vendor, tc.platform),
                                   tc.version))
            # Format manifest
            vp = defaultdict(set)  # vendor -> profile
            ps = defaultdict(set)  # profile -> script
            for s in sv:
                v, p, n = s.split(".")
                pn = "%s.%s" % (v, p)
                vp[v].add(pn)
                ps[pn].add(s)
            o = []
            for v in sorted(vp):
                o += ["# %s" % v]
                for p in sorted(vp[v]):
                    o += ["## %s" % p]
                    for sn in sorted(ps[p]):
                        o += ["### %s" % sn]
                        vs = defaultdict(set)  # platform -> version
                        for platform, version in sv[sn]:
                            vs[platform].add(version)
                        for platform in sorted(vs):
                            o += ["+ **%s:** %s" % (platform, ", ".join(sorted(vs[platform]))), ""]
            mf = "\n".join(o)
            path = os.path.join(self.local_repo_path(r), "README.md")
            print "Writing manifest for repo %s" % r.name
            safe_rewrite(path, mf)

    def handle_ensure_private(self, *args, **options):
        for p in args:
            if os.path.isfile(p):
                tc = BeefTestCase()
                tc.load_beef(p)
                if not tc.private:
                    tc.private = True
                    print "Marking %s as private" % p
                    tc.save_beef(p)

    def handle_create(self, *args, **options):
        if options.get("platform"):
            vendor, platform, version = options["platform"].split(",", 2)
        else:
            vendor, platform, version = None, None, None

        beef = {
            "type": "script::beef",
            "date": datetime.datetime.now().isoformat(),
            "script": options.get("script"),
            "guid": str(uuid.uuid4()),
            "vendor": vendor,
            "platform": platform,
            "version": version,
            "cli": {},
            "result": None
        }
        for cmd, result in zip(options["cli"], options["result"]):
            with open(result) as f:
                beef["cli"][cmd] = f.read()
        print json_encode(beef)