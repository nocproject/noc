# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# translation cli
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import subprocess
import argparse
import os
# Third-party modules
from babel.util import pathmatch
# NOC modules
from noc.core.management.base import BaseCommand
from noc.settings import LANGUAGES
from noc.config import config


class Command(BaseCommand):
    SERVICES = {
        "bi": {
            "messages": [
                "services/bi/**.py",
                "services/bi/**.html.j2",
                "core/bi/models/**.py"
            ],
            "messages_js": ["ui/bi/bi.js"]
        },
        "card": {
            "messages": [
                "services/card/**.py",
                "services/card/**.html.j2"
            ],
            "messages_js": ["ui/card/**.js"]
        },
        "login": {
            "messages": ["services/login/**.py"],
            "messages_js": ["ui/login/**.js"]
        },
        "web": {
            "messages": [
                "services/web/apps/**.py",
                "lib/app/**.py"
            ],
            "messages_js": ["ui/web/**.js"]
        }
    }

    TRANSLATIONS = [x[0] for x in LANGUAGES if x[0] != "en"]

    BABEL_CFG = config.path.babel_cfg
    BABEL = config.path.babel
    POJSON = config.path.pojson
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
        #
        edit_parser = subparsers.add_parser("edit")
        edit_parser.add_argument(
            "service",
            nargs=1,
            help="Service to edit"
        )
        edit_parser.add_argument(
            "language",
            nargs=1,
            help="Language to translate"
        )

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def glob(self, expr):
        if not hasattr(self, "_files"):
            # @fixme: Remove hg
            f = subprocess.Popen(
                ["./bin/hg", "locate"],
                stdout=subprocess.PIPE
            ).stdout
            self._files = f.read().splitlines()
        return [p for p in self._files if pathmatch(expr, p)]

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
                args = [
                    self.BABEL, "extract",
                    "-F", self.BABEL_CFG,
                    "--sort-by-file",
                    "--project=%s" % self.PROJECT,
                    "--copyright-holder=%s" % self.COPYRIGHT,
                    "-o", "%s/%s.pot" % (t_dir, domain)
                ]
                if domain.endswith("_js"):
                    args += ["-k", "__"]
                for expr in self.SERVICES[svc][domain]:
                    if os.path.isfile(expr):
                        args += [expr]
                    else:
                        args += self.glob(expr)
                subprocess.check_call(args)

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
                            "-l", lang,
                            "--previous"
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
                        jsp = os.path.join("ui", svc, "translations")
                        js = os.path.join(jsp, "%s.json" % lang)
                        if not os.path.isdir(jsp):
                            os.makedirs(jsp)
                        print("compiling catalog '%s' to '%s'" % (
                            po, js
                        ), file=self.stdout)
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

    def handle_edit(self, service=None, language=None, *args, **options):
        pfx = os.path.join("services", service[0],
                           "translations", language[0], "LC_MESSAGES")

        for path in [
            os.path.join(pfx, "messages.po"),
            os.path.join(pfx, "messages_js.po")
        ]:
            subprocess.check_call(["open", path])

if __name__ == "__main__":
    Command().run()
