# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NOC components versions
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os

## Version cache
_version = None


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
