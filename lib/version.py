# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NOC components versions
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Pytho modules
from __future__ import with_statement
import re

# Regular expressions
rx_ver_split = re.compile(r"^(?P<major>\d+)\.(?P<minor>\d+)(?:\.(?P<release>\d+))?(?:\((?P<interim>\d+)\)(?:r(?P<changeset>\d+))?)?$")
# Version cache
_version = None


def get_version():
    """
    Returns NOC version. Version format is X.Y[.Z][(I)[rREV]]
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
            lr = localrepo.localrepository(ui.ui(), path=".")  # Repo
            tip = lr.changelog.tip()  # tip revision
            tags = lr.tags()
            if "tip" in tags:
                del tags["tip"]
            if tip not in tags.values():
                # Add changeset if not tagged revision
                rev = lr.changelog.rev(lr.changelog.tip())
                v += "r%s" % rev
        except:
            pass
    except ImportError:
        pass
    # Save to cache
    _version = v
    return v


def split_version(v):
    """
    Split version string into tuple
    :param v: version string
    :returns: tuple of (major, minor, release, interim, changeset)
              where major and minor are integers
              release, interim or changeset are integers or None
    
    >>> split_version('0.7')
    (0, 7, None, None, None)
    >>> split_version('0.7.1(12)r4995')
    (0, 7, 1, 12, 4995)
    """
    match = rx_ver_split.match(v)
    if not match:
        raise ValueError("Invalid version: %s" % v)
    g = match.groupdict()
    release = int(g["release"]) if g["release"] is not None else None
    return (
        int(g["major"]), int(g["minor"]),
        release if release else None,
        int(g["interim"]) if g["interim"] is not None else None,
        int(g["changeset"]) if g["changeset"] is not None else None
    )


def cmp_version(v1, v2):
    """
    cmp()-like function for version comparison
    """
    s1 = [x if x is not None else 0 for x in split_version(v1)]
    s2 = [x if x is not None else 0 for x in split_version(v2)]
    # Compare major, minor and release
    r = cmp(s1[:3], s2[:3])
    if r != 0:
        return r
    # Compare interim
    c1 = s1[3]
    c2 = s2[3]
    if c1 != c2:
        if c1 == 0:
            return 1
        if c2 == 0:
            return -1
        return cmp(c1, c2)
    # Compare changeset
    c1 = s1[4]
    c2 = s2[4]
    if c1 != c2:
        if c1 == 0:
            return 1
        if c2 == 0:
            return -1
    return cmp(c1, c2)
