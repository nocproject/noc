# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NOC components versions
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from __future__ import with_statement


# Version cache
_version = None


def get_version():
    """
    Returns NOC version. Version format is X.Y.Z[rREV]
    >>> len(get_version())>0
    True
    """
    global _version
    # Try to get from cache
    if _version:
        return _version
    # Calculate version
    with open("VERSION") as f:
        v = f.read().split("\n")[0].strip()
    try:
        from mercurial import ui, localrepo
        try:
            lr = localrepo.localrepository(ui.ui(), path=".")
            rev = lr.changelog.rev(lr.changelog.tip())
            v += "r%s" % rev
        except:
            pass
    except ImportError:
        pass
    # Save to cache
    _version = v
    return v
