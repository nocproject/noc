# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Import managed objects from rancid
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
from optparse import make_option
import subprocess
import re
import datetime
import itertools
import os
## Django modules
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
## Third-party modules
import pytz
## NOC modules
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.sa.models.activator import Activator
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.sa.models.managedobject import ManagedObject
from noc.lib.gridvcs.gridvcs import GridVCS
import noc.settings

logger = logging.getLogger("main")
TZ = pytz.timezone(noc.settings.TIME_ZONE)
TMP = "/tmp/noc-import-rancid"


class Command(BaseCommand):
    """
    Manage Jobs
    """
    help = "Import data from rancid"
    option_list = BaseCommand.option_list + (
        make_option(
            "--routerdb",
            action="append",
            dest="routerdb",
            help="Path to the router.db"
        ),
        make_option(
            "--cloginrc",
            action="append",
            dest="cloginrc",
            help="Path to the .cloginrc"
        ),
        make_option(
            "--hosts",
            action="append",
            dest="hosts",
            help="Path to the /etc/hosts"
        ),
        make_option(
            "--repo",
            action="store",
            dest="repo",
            help="CVS repository"
        ),
        make_option(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            help="Check only, do not write to database"
        ),
        make_option(
            "--tags",
            action="append",
            dest="tags",
            help="Mark created managed objects by tags"
        ),
        make_option(
            "--profile",
            action="store",
            dest="object_profile",
            help="Set managed object profile for created objects",
            default="default"
        ),
        make_option(
            "--domain",
            action="store",
            dest="domain",
            help="Set administrative domain for created objects",
            default="default"
        ),
        make_option(
            "--activator",
            action="store",
            dest="activator",
            help="Set activator for created objects",
            default="default"
        ),
    )

    PROFILE_MAP = {
        "cisco": "Cisco.IOS",
        "juniper": "Juniper.JUNOS"
    }

    rx_f = re.compile(
        r"^RCS file: (?P<file>.+?),v$",
        re.MULTILINE | re.DOTALL
    )

    rx_fn = re.compile(
        r"^Working file: (?P<fn>.+?)$",
        re.MULTILINE | re.DOTALL
    )

    rx_rev = re.compile(
        r"^-----+\n"
        r"revision (?P<rev>\S+)\n"
        r"date: (?P<date>\S+ \S+(?: \S+)?);.+? state: (?P<state>\S+)",
        re.MULTILINE | re.DOTALL
    )

    def parse_hosts(self, hosts):
        """
        Parse /etc/hosts
        :returns: dict of name -> ip
        """
        r = {}
        for path in hosts:
            logger.info("Reading hosts from %s", path)
            with open(path) as f:
                for line in f.readlines():
                    if "#" in line:
                        line = line.split("#", 1)[0]
                    line = line.strip()
                    if not line:
                        continue
                    if ":" in line:
                        # Skip IPv6
                        continue
                    parts = line.split()
                    for p in parts[1:]:
                        r[p] = parts[0]
        return r

    def parse_routerdb(self, routerdb):
        rdb = {}  # Name -> profile
        for path in routerdb:
            logger.info("Reading routers from %s", path)
            with open(path) as f:
                for line in f.readlines():
                    if "#" in line:
                        line = line.split("#", 1)[0]
                    line = line.strip()
                    if not line:
                        continue
                    r = line.split(":")
                    if len(r) != 3:
                        continue
                    name, t, s = r
                    if s != "up":
                        logger.debug("Skipping %s", name)
                        continue
                    p = self.PROFILE_MAP.get(t)
                    if not p:
                        logger.info("Unknown type '%s'. Skipping", t)
                        continue
                    rdb[name] = p
        return rdb

    def parse_cloginrc(self, cloginrc):
        login = {}
        defaults = {}
        for path in cloginrc:
            logger.info("Reading cloginrc from %s", path)
            with open(path) as f:
                for line in f.readlines():
                    if "#" in line:
                        line = line.split("#", 1)[0]
                    line = line.strip()
                    if not line:
                        continue
                    line = line.replace("\t", " ")
                    r = line.split()
                    if len(r) > 4:
                        op, v, host = r[:3]
                        value = " ".join(r[3:])
                    elif len(r) == 3:
                        op, v, value = r
                        defaults[v] = value
                        continue
                    else:
                        op, v, host, value = r
                    if op != "add":
                        continue
                    if host not in login:
                        login[host] = {}
                    login[host][v] = value
        return login, defaults

    def index_cvs(self, repo):
        r = {}  # path -> (revision, date)
        p = subprocess.Popen(
            ["cvs", "log"],
            cwd=repo,
            stdout=subprocess.PIPE
        )
        data = p.stdout.read()
        parts = self.rx_f.split(data)[2::2]
        for data in parts:
            match = self.rx_fn.search(data)
            if not match:
                continue
            fn = match.group("fn")
            r[fn] = []
            for match in self.rx_rev.finditer(data):
                if match.group("state").lower() == "dead":
                    continue  # Ignore object replacement
                rev = match.group("rev")
                date = match.group("date")
                ds = date.split()
                if "/" in ds[0]:
                    fmt = "%Y/%m/%d %H:%M:%S"
                else:
                    fmt = "%Y-%m-%d %H:%M:%S"
                if len(ds) == 3:
                    # Date with TZ
                    date = "%s %s" % (ds[0], ds[1])
                r[fn] += [(
                    rev,
                    TZ.normalize(
                        pytz.utc.localize(
                            datetime.datetime.strptime(
                                date,
                                fmt
                            )
                        )
                    )
                )]
        return r

    def handle(self, *args, **options):
        if options["verbosity"] >= 2:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
        if not options["routerdb"]:
            raise CommandError("No routerdb given")
        if not options["cloginrc"]:
            raise CommandError("No cloginrc given")
        if not options["hosts"]:
            options["hosts"] = ["/etc/hosts"]
        if not options["repo"]:
            raise CommandError("No CVS repository")
        if not options["object_profile"]:
            raise CommandError("No object profile set")
        try:
            object_profile = ManagedObjectProfile.objects.get(
                name=options["object_profile"].strip())
        except ManagedObjectProfile.DoesNotExist:
            raise CommandError("Invalid object profile: %s" % options["object_profile"])
        if not options["domain"]:
            raise CommandError("No administrative domain set")
        try:
            domain = AdministrativeDomain.objects.get(
                name=options["domain"].strip())
        except AdministrativeDomain.DoesNotExist:
            raise CommandError("Invalid administrative domain: %s" % options["domain"])
        if not options["activator"]:
            raise CommandError("No activatorset")
        try:
            activator = Activator.objects.get(
                name=options["domain"].strip())
        except Activator.DoesNotExist:
            raise CommandError("Invalid activator: %s" % options["activator"])
        tags = []
        if options["tags"]:
            for t in options["tags"]:
                tags += [x.strip() for x in t.split(",")]
        self.dry_run = bool(options["dry_run"])
        #
        if not os.path.isdir(TMP):
            os.mkdir(TMP)
        #
        revisions = self.index_cvs(options["repo"])
        # Read configs
        hosts = self.parse_hosts(options["hosts"])
        rdb = self.parse_routerdb(options["routerdb"])
        login, ldefaults = self.parse_cloginrc(options["cloginrc"])
        # Process data
        n = 1
        count = len(rdb)
        for name in sorted(rdb):
            logger.debug("[%s/%s] Processing host %s", n, count, name)
            n += 1
            profile = rdb[name]
            address = hosts.get(name)
            if not address:
                # @todo: Resolve
                logger.info("Cannot resolve address for %s. Skipping", name)
                continue
            ld = login.get(name, ldefaults)
            if not ld:
                logger.info("No credentials for %s. Skipping", name)
                continue
            user = ld.get("user")
            password = ld.get("password")
            if "method" in ld and "ssh" in ld["method"]:
                method = "ssh"
            else:
                method = "telnet"
            logger.info("Managed object found: %s (%s, %s://%s@%s/)",
                        name, profile, method, user, address)
            if not self.dry_run:
                try:
                    mo = ManagedObject.objects.get(
                        Q(name=name) | Q(address=address)
                    )
                    logger.info("Already in the database")
                except ManagedObject.DoesNotExist:
                    logger.info("Creating managed object %s", name)
                    mo = ManagedObject(
                        name=name,
                        object_profile=object_profile,
                        administrative_domain=domain,
                        activator=activator,
                        scheme=1 if method == "ssh" else 0,
                        address=address,
                        profile_name=profile,
                        user=user,
                        password=password,
                        trap_source_ip=address,
                        tags=tags
                    )
                    mo.save()
            if name not in revisions:
                logger.error("Cannot find config for %s", name)
                continue
            if not self.dry_run:
                self.import_revisions(options["repo"], mo, name, revisions[name])

    def get_diff(self, repo, name, r0, r1):
        p = subprocess.Popen(
            ["cvs", "diff", "-r%s" % r0, "-r%s" % r1, name],
            cwd=repo,
            stdout=subprocess.PIPE
        )
        return p.stdout.read()

    def import_revisions(self, repo, mo, name, revisions):
        """
        Import CVS file revisions
        """
        def write_file(path, data):
            with open(path, "w") as f:
                f.write(data)

        # Prepare all config revisions
        with open(os.path.join(repo, name)) as f:
            path = os.path.join(TMP, "%s@%s" % (name, revisions[0][0]))
            logger.debug("writing %s", path)
            data = f.read()
            write_file(path, data)
            write_file(
                os.path.join(TMP, name),
                data
            )
        a, b = itertools.tee(revisions)
        next(b, None)
        for r0, r1 in itertools.izip(a, b):
            path = os.path.join(TMP, "%s@%s" % (name, r1[0]))
            logger.debug("writing %s", path)
            try:
                subprocess.check_call(
                    "(cvs diff -r%s -r%s %s | patch %s) && cp %s %s" % (
                        r0[0], r1[0], name,
                        os.path.join(TMP, name),
                        os.path.join(TMP, name),
                        os.path.join(TMP, "%s@%s" % (name, r1[0]))
                    ),
                    cwd=repo,
                    shell=True
                )
            except subprocess.CalledProcessError, why:
                logger.error("Failed to import %s@%s. Giving up",
                             name, r1[0])
                logger.error("CVS reported: %s", why)
                return
        # Import all config revisions
        gridvcs = GridVCS("config")
        for rev, date in reversed(revisions):
            logger.debug("   ... Importing %s@%s" % (name, rev))
            path = os.path.join(TMP, "%s@%s" % (name, rev))
            with open(path, "r") as f:
                data = f.read()
            if not self.dry_run:
                gridvcs.put(mo.id, data, ts=date)
        # Cleanup
        subprocess.check_call(
            "rm -f %s*" % name,
            cwd=TMP,
            shell=True
        )
