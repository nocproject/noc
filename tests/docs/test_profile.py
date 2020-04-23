# ----------------------------------------------------------------------
# <describe module here>
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import glob
import os

# Third-party modules
import cachetools
import pytest


@cachetools.cached({})
def all_vendors():
    r = []
    for path in glob.glob("sa/profiles/*"):
        vendor = path.split(os.sep)[-1]
        if vendor == "Generic" or ".py" in vendor:
            continue
        r += [vendor]
    return r


@cachetools.cached({})
def all_profiles():
    r = set()
    for path in glob.glob("sa/profiles/*/*/*.py"):
        vendor, profile = path.split(os.sep)[-3:-1]
        if vendor == "Generic":
            continue
        profile = "%s.%s" % (vendor, profile)
        r.add(profile)
    return list(r)


@pytest.mark.parametrize("vendor", all_vendors())
def test_vendor_doc_exists(vendor):
    path = os.path.join("docs", "src", "en", "profiles", "vendor-%s.rst" % vendor)
    assert os.path.exists(path), "Vendor '%s' must be documented in '%s'" % (vendor, path)


@pytest.mark.parametrize("profile", all_profiles())
def test_profile_doc_exists(profile):
    path = os.path.join("docs", "src", "en", "profiles", "%s.rst" % profile)
    assert os.path.exists(path), "Profile '%s' must be documented in '%s'" % (profile, path)
