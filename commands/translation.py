# ----------------------------------------------------------------------
# translation cli
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import subprocess
import argparse
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

# Third-party modules
from babel.util import pathmatch
from functools import cache

# NOC modules
from noc.core.management.base import BaseCommand
from noc.settings import LANGUAGES
from noc.core.comp import smart_text

BABEL_CFG = b"""# Translation extraction config
[python: **.py]

[javascript: **.js]
extract_messages = _, __

[jinja2: **.j2]
extensions=jinja2.ext.autoescape,jinja2.ext.with_
"""

BABEL = "pybabel"
POJSON = "pojson"


class Command(BaseCommand):
    SERVICES = {
        # "bi": {
        #    "messages": ["services/bi/**.py", "services/bi/**.html.j2", "bi/models/**.py"],
        #    "messages_js": ["ui/bi2/bi.js"],
        # },
        "card": {
            "messages": ["services/card/**.py", "services/card/**.html.j2"],
            "messages_js": ["ui/card/**.js"],
        },
        "login": {"messages": ["services/login/**.py"], "messages_js": ["ui/login/**.js"]},
        "web": {
            "messages": ["services/web/apps/**.py", "core/**.py"],
            "messages_js": ["ui/web/**.js"],
        },
    }

    TRANSLATIONS = [x[0] for x in LANGUAGES if x[0] != "en"]

    PROJECT = "The NOC Project"
    COPYRIGHT = "The NOC Project"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        #
        extract_parser = subparsers.add_parser("extract")
        extract_parser.add_argument(
            "services", nargs=argparse.REMAINDER, help="Services to extract"
        )
        #
        update_parser = subparsers.add_parser("update")
        update_parser.add_argument("services", nargs=argparse.REMAINDER, help="Services to update")
        #
        update_parser = subparsers.add_parser("compile")
        update_parser.add_argument("services", nargs=argparse.REMAINDER, help="Services to compile")
        #
        edit_parser = subparsers.add_parser("edit")
        edit_parser.add_argument("service", nargs=1, help="Service to edit")
        edit_parser.add_argument("language", nargs=1, help="Language to translate")

    def handle(self, cmd, *args, **options):
        return getattr(self, f"handle_{cmd}")(*args, **options)

    def glob(self, expr):
        return [smart_text(p) for p in ls() if pathmatch(expr, smart_text(p))]

    def handle_extract(self, services=None):
        if not services:
            services = sorted(self.SERVICES)
        for svc in services:
            if svc not in self.SERVICES:
                self.die(f"Unknown service: {svc}")
            t_dir = Path("services", svc, "translations")
            if not t_dir.exists():
                os.makedirs(t_dir)
            with NamedTemporaryFile() as cfg:
                cfg.write(BABEL_CFG)
                cfg.flush()
                for domain in self.SERVICES[svc]:
                    pot = (t_dir / domain).with_suffix(".pot")
                    args = [
                        "extract",
                        "-F",
                        cfg.name,
                        "--sort-by-file",
                        f"--project={self.PROJECT}",
                        f"--copyright-holder={self.COPYRIGHT}",
                        "-o",
                        pot,
                    ]
                    if domain.endswith("_js"):
                        args += ["-k", "__"]
                    for expr in self.SERVICES[svc][domain]:
                        if os.path.isfile(expr):
                            args += [expr]
                        else:
                            args += self.glob(expr)
                    self.babel(*tuple(args))

    def handle_update(self, services=None):
        if not services:
            services = sorted(self.SERVICES)
        for svc in services:
            if svc not in self.SERVICES:
                self.die(f"Unknown service: {svc}")
            t_dir = Path("services", svc, "translations")
            for domain in self.SERVICES[svc]:
                pot = t_dir / f"{domain}.pot"
                for lang in self.TRANSLATIONS:
                    po = (t_dir / lang / "LC_MESSAGES" / domain).with_suffix(".po")
                    if not po.exists():
                        self.babel(
                            "init",
                            "-i",
                            pot,
                            f"--domain={domain}",
                            "-d",
                            t_dir,
                            "-l",
                            lang,
                        )
                    else:
                        self.babel(
                            "update",
                            "-i",
                            pot,
                            f"--domain={domain}",
                            "-d",
                            t_dir,
                            "-l",
                            lang,
                            "--previous",
                        )

    def handle_compile(self, services=None):
        if not services:
            services = sorted(self.SERVICES)
        for svc in services:
            if svc not in self.SERVICES:
                self.die(f"Unknown service: {svc}")
            t_dir = Path("services", svc, "translations")
            for domain in self.SERVICES[svc]:
                for lang in self.TRANSLATIONS:
                    po = (t_dir / lang / "LC_MESSAGES" / domain).with_suffix(".po")
                    if domain.endswith("_js"):
                        jsp = Path("ui", svc, "translations")
                        js = (jsp / lang).with_suffix(".json")
                        if not os.path.isdir(jsp):
                            os.makedirs(jsp)
                        print(f"compiling catalog '{po}' to '{js}'", file=self.stdout)
                        with open(js, "w") as fp:
                            subprocess.check_call([POJSON, "-p", po], stdout=fp)
                    else:
                        mo = (t_dir / lang / "LC_MESSAGES" / domain).with_suffix(".mo")
                        subprocess.check_call([BABEL, "compile", "-i", po, "-o", mo])

    @staticmethod
    def handle_edit(self, service=None, language=None):
        pfx = Path("services", service[0], "translations", language[0], "LC_MESSAGES")

        for po in ["messages", "messages_js"]:
            path = (pfx / po).with_suffix(".po")
            subprocess.check_call(["open", str(path)])

    @staticmethod
    def babel(*args: tuple[str]) -> None:
        args = [BABEL] + [str(x) for x in args]
        subprocess.check_call(args)


@cache
def ls() -> list[str]:
    f = subprocess.Popen(["git", "ls-files"], stdout=subprocess.PIPE).stdout
    return f.read().splitlines()


if __name__ == "__main__":
    Command().run()
