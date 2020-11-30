# ----------------------------------------------------------------------
# Test profile docs
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import glob
import os

# Third-party modules
import cachetools
import pytest

XFAIL_VENDORS = {"OS"}


@cachetools.cached({})
def all_vendors():
    r = []
    for path in glob.glob("sa/profiles/*"):
        vendor = path.split(os.sep)[-1]
        if (
            vendor == "Generic"
            or ".py" in vendor
            or vendor.startswith(".")
            or vendor.startswith("_")
        ):
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
    if vendor in XFAIL_VENDORS:
        pytest.xfail("Excluded")
    path = os.path.join("docs", "en", "docs", "reference", "profiles", vendor, "index.md")
    assert os.path.exists(path), "Vendor '%s' must be documented in '%s'" % (vendor, path)


@pytest.mark.parametrize("vendor", all_vendors())
def test_vendor_doc_toc(toc, vendor):
    if vendor in XFAIL_VENDORS:
        pytest.xfail("Excluded")
    path = ["Reference", "Profiles", vendor, "Overview"]
    assert path in toc
    v = toc[path].split("/")
    assert v == ["reference", "profiles", vendor, "index.md"]


@pytest.mark.parametrize("profile", all_profiles())
def test_profile_doc_exists(profile):
    vendor = profile.split(".")[0]
    path = os.path.join("docs", "en", "docs", "reference", "profiles", vendor, f"{profile}.md")
    assert os.path.exists(path), "Profile '%s' must be documented in '%s'" % (profile, path)
