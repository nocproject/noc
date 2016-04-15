# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## translation cli
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import subprocess
import argparse
import os
import glob
## NOC modules
from noc.core.management.base import BaseCommand


class Command(BaseCommand):
    SERVICES = {
        "card": {
            "messages": ["services/card/"],
            "messages_js": ["ui/card/"]
        },
        "login": {
            "messages": ["services/login"],
            "messages_js": ["ui/login/"]
        },
        "web": {
            "messages": ["*/apps/*.py"],
            "messages_js": ["*/apps/*/js/**.js"]
        }
    }

    TRANSLATIONS = ["ru"]

    BABEL_CFG = "etc/babel.cfg"
    BABEL = "./bin/pybabel"
    POJSON = "./bin/pojson"
    PROJECT = "The NOC Project"
    COPYRIGHT = "The NOC Project"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        #
        extract_parser = subparsers.add_parser("extract")
        extract_parser.add_argument(
            "services",
            nargs=argparse.REMAINDER,
            help="Services to extract"
        )
        #
        update_parser = subparsers.add_parser("update")
        update_parser.add_argument(
            "services",
            nargs=argparse.REMAINDER,
            help="Services to update"
        )
        #
        update_parser = subparsers.add_parser("compile")
        update_parser.add_argument(
            "services",
            nargs=argparse.REMAINDER,
            help="Services to compile"
        )

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_extract(self, services=None, *args, **options):
        if not services:
            services = sorted(self.SERVICES)
        for svc in services:
            if svc not in self.SERVICES:
                self.die("Unknown service: %s" % svc)
            t_dir = "services/%s/translations" % svc
            if not os.path.exists(t_dir):
                os.makedirs(t_dir)
            for domain in self.SERVICES[svc]:
                src = []
                for expr in self.SERVICES[svc][domain]:
                    src += glob.glob(expr)
                subprocess.check_call([
                    self.BABEL, "extract",
                    "-F", self.BABEL_CFG,
                    "--sort-by-file",
                    "--project=%s" % self.PROJECT,
                    "--copyright-holder=%s" % self.COPYRIGHT,
                    "-o", "%s/%s.pot" % (t_dir, domain)
                ] + src)

    def handle_update(self, services=None, *args, **options):
        if not services:
            services = sorted(self.SERVICES)
        for svc in services:
            if svc not in self.SERVICES:
                self.die("Unknown service: %s" % svc)
            t_dir = "services/%s/translations" % svc
            for domain in self.SERVICES[svc]:
                pot = os.path.join(t_dir, "%s.pot" % domain)
                for lang in self.TRANSLATIONS:
                    po = os.path.join(
                        t_dir, lang, "LC_MESSAGES", "%s.po" % domain
                    )
                    if not os.path.exists(po):
                        subprocess.check_call([
                            self.BABEL, "init",
                            "-i", pot,
                            "--domain=%s" % domain,
                            "-d", t_dir,
                            "-l", lang
                        ])
                    else:
                        subprocess.check_call([
                            self.BABEL, "update",
                            "-i", pot,
                            "--domain=%s" % domain,
                            "-d", t_dir,
                            "-l", lang
                        ])

    def handle_compile(self, services=None, *args, **options):
        if not services:
            services = sorted(self.SERVICES)
        for svc in services:
            if svc not in self.SERVICES:
                self.die("Unknown service: %s" % svc)
            t_dir = "services/%s/translations" % svc
            for domain in self.SERVICES[svc]:
                for lang in self.TRANSLATIONS:
                    po = os.path.join(
                        t_dir, lang, "LC_MESSAGES", "%s.po" % domain
                    )
                    if domain.endswith("_js"):
                        js = os.path.join(
                            t_dir, lang, "LC_MESSAGES",
                            "%s.json" % domain
                        )
                        print "compiling catalog '%s' to '%s'" % (
                            po, js
                        )
                        with open(js, "w") as f:
                            subprocess.check_call([
                                self.POJSON,
                                "-p",
                                po
                            ], stdout=f)
                    else:
                        mo = os.path.join(
                            t_dir, lang, "LC_MESSAGES", "%s.mo" % domain
                        )
                        subprocess.check_call([
                            self.BABEL, "compile",
                            "-i", po,
                            "-o", mo
                        ])

if __name__ == "__main__":
    Command().run()
