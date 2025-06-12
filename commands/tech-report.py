# ---------------------------------------------------------------------
# Display system and dependencies information
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
# Using:
# ./noc tech-report system
# ./noc tech-report dependencies
# ./noc tech-report
# ./noc tech-report --ansi-symbols system
# and so on

# Python modules
from importlib import metadata
import os
from pathlib import Path
import re
import subprocess
import sys
from dataclasses import dataclass
from enum import IntEnum, auto
from collections import defaultdict
from typing import Dict, DefaultDict

# NOC modules
from noc.config import config
from noc.core.management.base import BaseCommand
from noc.core.version import version

# Obtained from the `colorama` python-library
# see also: https://en.wikipedia.org/wiki/ANSI_escape_code
CSI = "\033["
FORE_GREEN = f"{CSI}{str(32)}m"
FORE_RED = f"{CSI}{str(31)}m"
FORE_BLUE = f"{CSI}{str(34)}m"
STYLE_RESET_ALL = f"{CSI}{str(0)}m"


class LibStatus(IntEnum):
    """
    Library status.

    Attributes:
        OK: Library is ok.
        MISMATCH: Version mismatch.
        MISSED: Library is mandatory, but missed.
        SKIP: Library is optional and skipped.
    """

    OK = auto()
    MISMATCH = auto()
    MISSED = auto()
    SKIPPED = auto()


@dataclass
class Library(object):
    original_name: str
    req_version: str
    inst_version: str = ""
    node: bool = False

    @property
    def status(self) -> LibStatus:
        if self.inst_version:
            if self.req_version == self.inst_version:
                return LibStatus.OK
            return LibStatus.MISMATCH
        if self.node:
            return LibStatus.MISSED
        return LibStatus.SKIPPED

    def get_flag(self, is_ansi: bool = False) -> str:
        if is_ansi:
            return _ANSI_FLAGS[self.status]
        return _UNICODE_FLAGS[self.status]


_ANSI_FLAGS = {
    LibStatus.OK: "v",
    LibStatus.MISMATCH: "x",
    LibStatus.MISSED: "?",
    LibStatus.SKIPPED: "-",
}

_UNICODE_FLAGS = {
    LibStatus.OK: f"{FORE_GREEN}\u2705{STYLE_RESET_ALL}",
    LibStatus.MISMATCH: f"{FORE_RED}\u274c{STYLE_RESET_ALL}",
    LibStatus.MISSED: f"{FORE_RED}\uff1f{STYLE_RESET_ALL}",
    LibStatus.SKIPPED: f"{FORE_BLUE}\u2796{STYLE_RESET_ALL}",
}


class Command(BaseCommand):
    help = "Display system and dependencies information"
    is_ansi = False

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        parser.add_argument(
            "-a", "--ansi-symbols", action="store_true", help="Use ANSI instead of Unicode symbols"
        )
        subparsers.add_parser("system", help="Display system information")
        subparsers.add_parser("dependencies", help="Display dependencies")

    def handle(self, ansi_symbols, *args, **options):
        if ansi_symbols:
            self.is_ansi = True
        cmd = options.pop("cmd")
        cmd = cmd or "total"
        return getattr(self, f'handle_{cmd.replace("-", "_")}')(*args, **options)

    def handle_total(self, *args, **options):
        self.handle_system(*args, **options)
        self.handle_dependencies(*args, **options)

    @property
    def flags(self) -> Dict[LibStatus, str]:
        if self.is_ansi:
            return _ANSI_FLAGS
        return _UNICODE_FLAGS

    def handle_system(self, *args, **options):
        OK = self.flags[LibStatus.OK]
        SKIPPED = self.flags[LibStatus.SKIPPED]
        self.print("System information")
        self.print("==================")
        self.print(f"NOC version       : {version.version}")
        self.print(f"Python version    : {sys.version}")
        self.print(f"Installation name : {config.installation_name}")
        custom_path = config.path.custom_path
        if custom_path:
            cp_exists = f"exists {OK}" if os.path.exists(custom_path) else f"NOT exists {SKIPPED}"
            self.print(f"Custom path       : {config.path.custom_path} ({cp_exists})")
            custom_revision = "-"
            if os.path.exists(custom_path):
                try:
                    custom_revision = subprocess.check_output(
                        ["cat", ".git/HEAD"], cwd=custom_path, encoding="utf-8"
                    )
                    if custom_revision.endswith("\n"):
                        custom_revision = custom_revision[:-1]
                except subprocess.CalledProcessError:
                    pass
            self.print(f"Custom revision   : {custom_revision}")
        else:
            self.print("Custom path       : ---")
            self.print("Custom revision   : ---")
        self.print("")

    REQUIREMENTS_PATH = ".requirements"
    rx = re.compile(r"^(?P<lib_name>[a-zA-Z][-a-zA-Z0-9_]*)\[*.*]*==(?P<version>[a-zA-Z0-9.]+).*$")

    def handle_dependencies(self, *args, **options):
        def lib_key(s: str) -> str:
            return s.lower().replace("-", "_")

        def n_status(s: LibStatus) -> str:
            n = summary[s]
            if n:
                return f": {n}"
            return ""

        self.print("Dependencies")
        self.print("============")
        # Get required versions
        root_path = Path(self.REQUIREMENTS_PATH)
        libraries: dict[str, Library] = {}
        for fp in root_path.glob("*.txt"):
            if not fp.is_file:
                continue
            with open(fp, "r") as f:
                btext = f.read()
                lines = btext.split("\n")
            for line in lines:
                match = self.rx.match(line)
                if match:
                    lib_name, req_version = match.groups()
                    libraries[lib_key(lib_name)] = Library(
                        original_name=lib_name, req_version=req_version, node=fp.name == "node.txt"
                    )
        # Get installed versions
        for distribution in metadata.distributions():
            lib_name = lib_key(distribution.metadata["Name"])
            if lib_name in libraries:
                libraries[lib_name].inst_version = distribution.version
        # Display information
        col_lib_name, col_required, col_installed = 25, 25, 25
        summary: DefaultDict[LibStatus, int] = defaultdict(int)
        self.print(
            "   | "
            f"{'Library':{col_lib_name}} | {'Required':{col_required}} | "
            f"{'Installed':{col_installed}}"
        )
        self.print(f"---|-{'-'*col_lib_name}-|-{'-'*col_required}-|-{'-'*col_installed}")
        for lib_name, lib_data in sorted(libraries.items(), key=lambda item: item[1].original_name):
            flag = lib_data.get_flag(self.is_ansi)
            self.print(
                f"{flag} | {lib_data.original_name:{col_lib_name }} | "
                f"{lib_data.req_version:{col_required}} | "
                f"{lib_data.inst_version:{col_installed}}"
            )
            summary[lib_data.status] += 1
        self.print("")
        self.print("Legend:")
        self.print(f"{self.flags[LibStatus.OK]} Library version is correct")
        self.print(
            f"{self.flags[LibStatus.MISMATCH]} Library version mismatch{n_status(LibStatus.MISMATCH)}"
        )
        self.print(
            f"{self.flags[LibStatus.MISSED]} Library is mandatory, but missing{n_status(LibStatus.MISSED)}"
        )
        self.print(f"{self.flags[LibStatus.SKIPPED]} Library is optional and missing")
        self.print("")


if __name__ == "__main__":
    Command().run()
