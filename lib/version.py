# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NOC components versions
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import sys
import subprocess
import platform
## NOC modules
from noc import settings


## Version cache
_version = None
BRANCH = None
TIP = None
OS_BRAND = None

if hasattr(subprocess, "check_output"):
    check_output = subprocess.check_output
else:
    def check_output(args):
        return subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]


def get_version():
    """
    Returns NOC version. Version formats are:
    * X.Y.Z -- releases
    * X.Y.Z-<tip> -- hotfixes
    * X.Y.Zpre<tip> -- pre-releases (release/* branch)
    * X.Y.Zdev<tip> -- develop
    :return:
    """
    global _version
    if _version:
        return _version
    # Get base version
    with open("VERSION") as f:
        v = f.read().split()[0].strip()
    if not os.path.isdir(".hg"):
        return v
    # Get branch
    try:
        from mercurial import ui, localrepo
    except ImportError:
        return v
    repo = localrepo.localrepository(ui.ui(), path=".")
    tip = repo.changelog.rev(repo.changelog.tip())
    branch = repo.dirstate.branch()
    if branch == "default":
        # Release
        _version = v
    elif branch.startswith("hotfix/"):
        # Hotfix
        _version = "%s-%s" % (v, tip)
    elif branch.startswith("release/"):
        # Release candidate
        _version = "%spre%s" % (v, tip)
    else:
        # Develop or feature branch
        _version = "%sdev%s" % (v, tip)
    return _version


def get_branch():
    global BRANCH

    if BRANCH:
        return BRANCH
    if os.path.exists(".hg/branch"):
        with open(".hg/branch") as f:
            BRANCH = f.read().strip()
    return BRANCH


def get_tip():
    global TIP

    if TIP:
        return TIP

    try:
        from mercurial import ui, localrepo
    except ImportError:
        return None
    repo = localrepo.localrepository(ui.ui(), path=".")
    TIP = repo.changelog.tip()[:6].encode("hex")
    return TIP


def get_os_brand():
    """
    Get OS brand
    :return:
    """
    def _get_brand():
        o = os.uname()[0].lower()
        if o == "linux":
            # First, try lsb_release -d
            try:
                b = check_output(["lsb_release", "-d"])
                return b.split(":", 1)[1].strip()
            except OSError:
                pass
            if os.path.exists("/etc/SuSE-release"):
                # SuSE
                with open("/etc/SuSE-release") as f:
                    return f.readline().strip()
        elif o == "freebsd":
            u = os.uname()
            return "%s %s" % (u[0], u[2])
        elif o == "darwin":
            # OS X
            return "Mac OS X %s" % platform.mac_ver()[0]
        return None

    global OS_BRAND

    if not OS_BRAND:
        OS_BRAND = _get_brand()
    return OS_BRAND


def get_os_version():
    return " ".join(os.uname())


def get_python_version():
    return sys.version.split()[0]


def get_pg_version():
    with os.popen("pg_config --version") as f:
        return f.read().strip().split(" ", 1)[1]


def get_mongo_version():
    try:
        import pymongo
    except ImportError:
        return ""
    connection_args = {}
    if settings.NOSQL_DATABASE_HOST:
        connection_args["host"] = settings.NOSQL_DATABASE_HOST
    if settings.NOSQL_DATABASE_PORT:
        connection_args["port"] = int(settings.NOSQL_DATABASE_PORT)
    c = pymongo.Connection(**connection_args)
    i = c.server_info()
    return "%s (%dbit)" % (i["version"], i["bits"])


def get_python_packages():
    o = check_output(["./bin/pip", "freeze"])
    return dict(l.split("==", 1) for l in o.splitlines() if "==" in l)


def get_versions():
    r = {
        "Python": get_python_version(),
        "PostgreSQL": get_pg_version(),
        "MongoDB": get_mongo_version()
    }
    r.update(get_python_packages())
    return r


def get_solutions():
    """
    Get installed solutions
    """
    r = []
    for sn in settings.config.options("solutions"):
        if settings.config.getboolean("solutions", sn):
            r += [[sn, None]]
    return r
