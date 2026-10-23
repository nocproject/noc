# ---------------------------------------------------------------------
# NOC components versions
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import sys
import subprocess
from pathlib import Path
from functools import cached_property

# NOC modules
from noc.config import config
from noc import __version__

CHANGESET_LEN = 8
WHICH = "which"


class Version:
    @cached_property
    def has_git(self) -> bool:
        """
        Check .git directory is exists and git executable is in $PATH
        :return:
        """
        if os.path.exists(".git"):
            with open(os.devnull, "w") as null:
                return subprocess.call([WHICH, "git"], stdout=null) == 0
        return False

    @cached_property
    def branch(self) -> str:
        """
        Returns current branch
        :return:
        """
        if self.has_git:
            try:
                return subprocess.check_output(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"], encoding="utf-8"
                ).strip()
            except subprocess.CalledProcessError as e:
                print(
                    f"Error when detect branch: {e}."
                    f" Please try execute 'git config --global --add safe.directory /opt/noc' on noc user"
                )
        return ""

    @cached_property
    def changeset(self) -> str:
        """
        Returns current changeset
        :return:
        """
        if self.has_git:
            try:
                return (subprocess.check_output(["git", "rev-parse", "HEAD"], encoding="utf-8"))[
                    :CHANGESET_LEN
                ]
            except subprocess.CalledProcessError as e:
                print(
                    f"Error when detect branch: {e}."
                    f" Please try execute 'git config --global --add safe.directory /opt/noc' on noc user"
                )
        return ""

    @cached_property
    def version(self) -> str:
        if not self.has_git:
            return __version__
        try:
            v = subprocess.check_output(
                ["git", "describe", "--tags", f"--abbrev={CHANGESET_LEN}"], encoding="utf-8"
            )
        except subprocess.CalledProcessError:
            return __version__  # Git is broken, fallback
        if "-" not in v:
            return v.strip()
        r = v.rsplit("-", 2)
        if len(r) < 3:
            return v.strip()
        v, n, cs = r
        kw = {
            "version": v,
            "branch": self.branch,
            "number": n,
            "changeset": cs[1 : CHANGESET_LEN + 1],
        }
        return config.version_format % kw

    @cached_property
    def os_version(self) -> str:
        return " ".join(os.uname())

    @cached_property
    def os_brand(self) -> str | None:
        uname = os.uname()
        match uname.sysname.lower():
            case "linux":
                os_release = Path("/etc/os-release")
                if not os_release.exists():
                    return "Unknown Linux"
                data: dict[str, str] = {}
                for line in os_release.read_text().splitlines():
                    if "=" in line:
                        k, v = line.split("=", 1)
                        data[k] = v.strip('"')
                return f"{data['NAME']} {data['VERSION_ID']}"
            case "freebsd":
                return f"{uname.sysname} {uname.release}"
            case _:
                return None

    @cached_property
    def process(self) -> str:
        argv = [v for v in sys.argv if v]
        if not argv:
            return sys.executable
        if argv[0].endswith("python") and len(argv) > 1:
            return argv[1]
        return argv[0]

    @cached_property
    def package_versions(self) -> dict[str, str]:
        return {"Python": sys.version.split()[0]}


# Singleton instance
version = Version()
