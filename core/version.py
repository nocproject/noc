# ---------------------------------------------------------------------
# NOC components versions
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import sys
import subprocess
import platform
from typing import Optional, Dict

# NOC modules
from noc.config import config

CHANGESET_LEN = 8
BRAND_PATH = config.get_customized_paths("BRAND", prefer_custom=True)
WHICH = "which"
if os.name == "nt":
    WHICH = "where"


class cachedproperty(object):
    def __init__(self, f):
        self.f = f
        self.n = "_%s" % f.__name__
        self.__doc__ = f.__doc__

    def __get__(self, instance, owner):
        if instance is None:
            return self
        v = getattr(instance, self.n, None)
        if v is None:
            v = self.f(instance)
            setattr(instance, self.n, v)
        return v


class Version(object):
    @cachedproperty
    def has_git(self) -> bool:
        """
        Check .git directory is exists and git executable is in $PATH
        :return:
        """
        if os.path.exists(".git"):
            with open(os.devnull, "w") as null:
                return subprocess.call([WHICH, "git"], stdout=null) == 0
        return False

    @cachedproperty
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

    @cachedproperty
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

    @cachedproperty
    def version(self) -> str:
        def static_version() -> str:
            """
            Read VERSION file
            """
            with open("VERSION") as f:
                return f.read().strip()

        if not self.has_git:
            return static_version()
        try:
            v = subprocess.check_output(
                ["git", "describe", "--tags", f"--abbrev={CHANGESET_LEN}"], encoding="utf-8"
            )
        except subprocess.CalledProcessError:
            return static_version()  # Git is broken, fallback
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

    @cachedproperty
    def brand(self) -> str:
        for p in BRAND_PATH:
            if os.path.exists(p):
                with open(p) as f:
                    return f.read().strip()
        return config.brand

    @cachedproperty
    def os_version(self) -> str:
        return " ".join(os.uname())

    @cachedproperty
    def os_brand(self) -> Optional[str]:
        o = os.uname()[0].lower()
        if o == "linux":
            # os-release
            if os.path.exists("/etc/os-release"):
                vdata = {}
                with open("/etc/os-release") as f:
                    for line in f:
                        if "=" not in line:
                            continue
                        line = line.strip()
                        k, v = line.split("=", 1)
                        if v.startswith('"') and v.endswith('"'):
                            v = v[1:-1]
                        vdata[k] = v
                return "%s %s" % (vdata["NAME"], vdata["VERSION_ID"])
            # Old SuSE?
            if os.path.exists("/etc/SuSE-release"):
                # SuSE
                with open("/etc/SuSE-release") as f:
                    return f.readline().strip()
            # try lsb_release -d
            try:
                b = subprocess.check_output(["lsb_release", "-d"], encoding="utf-8")
                return b.split(":", 1)[1].strip()
            except OSError:
                pass
            return "Unknown Linux"
        if o == "freebsd":
            u = os.uname()
            return "%s %s" % (u[0], u[2])
        if o == "darwin":
            # OS X
            return "Mac OS X %s" % platform.mac_ver()[0]
        return None

    @cachedproperty
    def python_version(self) -> str:
        return sys.version.split()[0]

    @cachedproperty
    def process(self) -> str:
        argv = [v for v in sys.argv if v]
        if not argv:
            return sys.executable
        if argv[0].endswith("python") and len(argv) > 1:
            return argv[1]
        return argv[0]

    @cachedproperty
    def package_versions(self) -> Dict[str, str]:
        return {"Python": self.python_version}


# Singleton instance
version = Version()
