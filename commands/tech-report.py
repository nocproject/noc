# ---------------------------------------------------------------------
# Display system and dependencies information
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from importlib import metadata
import os
from pathlib import Path
import re
import subprocess
import sys

# Third-party modules
from colorama import Fore, Style

# NOC modules
from noc.config import config
from noc.core.management.base import BaseCommand
from noc.core.version import version


class Command(BaseCommand):
    help = "Display system and dependencies information"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        subparsers.add_parser("system", help="Display system information")
        subparsers.add_parser("dependencies", help="Display dependencies")

    def handle(self, *args, **options):
        cmd = options.pop("cmd")
        cmd = cmd or "total"
        return getattr(self, f'handle_{cmd.replace("-", "_")}')(*args, **options)

    def handle_total(self, *args, **options):
        self.handle_system(*args, **options)
        self.handle_dependencies(*args, **options)

    flag_ok = f"{Fore.GREEN}\u2705{Style.RESET_ALL}"
    flag_error = f"{Fore.RED}\u274C{Style.RESET_ALL}"
    flag_missing = f"{Fore.BLUE}\u2796{Style.RESET_ALL}"

    def handle_system(self, *args, **options):
        self.print("System information")
        self.print("==================")
        self.print(f"NOC version       : {version.version}")
        self.print(f"Python version    : {sys.version}")
        self.print(f"Installation name : {config.installation_name}")
        custom_path = config.path.custom_path
        if custom_path:
            cp_exists = (
                f"exists {self.flag_ok}"
                if os.path.exists(custom_path)
                else f"NOT exists {self.flag_error}"
            )
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
        self.print("Dependencies")
        self.print("============")
        # Get required versions
        root_path = Path(self.REQUIREMENTS_PATH)
        libraries: dict[str, dict[str, str]] = {}
        count = 0
        for fp in root_path.glob("*.txt"):
            if not fp.is_file:
                continue
            f_node = fp.name == "node.txt"
            with open(fp, "r") as f:
                btext = f.read()
                lines = btext.split("\n")
            for line in lines:
                match = self.rx.match(line)
                if match:
                    lib_name, req_version = match.groups()
                    libraries[lib_name.lower()] = {
                        "original_name": lib_name,
                        "req_version": req_version,
                        "inst_version": "",
                        "node": f_node,
                    }
            count += 1
        # Get installed versions
        for distribution in metadata.distributions():
            lib_name = distribution.metadata["Name"].lower()
            if lib_name in libraries:
                libraries[lib_name]["inst_version"] = distribution.version
        # Sorting
        libraries: list[tuple[str, dict[str, str]]] = sorted(
            libraries.items(), key=lambda item: item[1]["original_name"]
        )
        # Display information
        col_lib_name, col_required, col_installed, col_node = 35, 25, 25, 25
        self.print(
            f"{'Library':{col_lib_name}} | {'Required':{col_required}} | "
            f"{'Installed':{col_installed}} | {'Node/necessary':{col_node}}"
        )
        self.print(
            f"{'-'*col_lib_name}-|-{'-'*col_required}-|-{'-'*col_installed}-|-{'-'*col_node}"
        )
        for lib_name, lib_data in libraries:
            if not lib_data["inst_version"]:
                flag = self.flag_missing
            else:
                flag = (
                    self.flag_ok
                    if lib_data["req_version"] == lib_data["inst_version"]
                    else self.flag_error
                )
            flag_additional = (
                self.flag_error if not lib_data["inst_version"] and lib_data["node"] else "  "
            )
            p_node = "YES" if lib_data["node"] else "-"
            self.print(
                f"{flag}{flag_additional} {lib_data['original_name']:{col_lib_name - 5}} | "
                f"{lib_data['req_version']:{col_required}} | "
                f"{lib_data['inst_version']:{col_installed}} | {p_node:{col_node}}"
            )
        self.print("")
        self.print("Legend:")
        self.print(f"{self.flag_ok}{'  '} Library version is correct")
        self.print(f"{self.flag_error}{'  '} Library version is incorrect")
        self.print(f"{self.flag_missing}{'  '} Library is missing")
        self.print(f"{self.flag_missing}{self.flag_error} Library is necessary, but missing")
        self.print("")


if __name__ == "__main__":
    Command().run()
