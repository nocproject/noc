# ----------------------------------------------------------------------
# Test profile docs
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from pathlib import Path

# Third-party modules
import cachetools
import pytest

# NOC modules
from noc.config import config

PROFILES_ROOT = config.noc_base / "sa" / "profiles"
PROFILE_DOCS_BASE = Path("docs", "profiles-reference")
XFAIL_VENDORS = {"OS"}


@cachetools.cached({})
def all_vendors() -> list[str]:
    r = []
    for path in PROFILES_ROOT.iterdir():
        if not path.is_dir():
            continue
        vendor = path.name
        if vendor == "Generic" or vendor.startswith(".") or vendor.startswith("_"):
            continue
        r.append(vendor)
    return r


@cachetools.cached({})
def all_profiles() -> list[str]:
    r = set()
    for py_file in PROFILES_ROOT.rglob("*/profile.py"):
        parts = py_file.relative_to(PROFILES_ROOT).parts
        if len(parts) < 3:
            continue
        vendor, profile_name = parts[0], parts[1]
        if vendor == "Generic":
            continue
        r.add(f"{vendor}.{profile_name}")
    return list(r)


@pytest.mark.parametrize("vendor", all_vendors())
def test_vendor_doc_exists(vendor):
    if vendor in XFAIL_VENDORS:
        pytest.xfail("Excluded")
    path = PROFILE_DOCS_BASE / vendor / "index.md"
    assert path.exists(), f"Vendor '{vendor}' must be documented in {path}"


@pytest.mark.parametrize("vendor", all_vendors())
def test_vendor_doc_toc(toc, vendor):
    if vendor in XFAIL_VENDORS:
        pytest.xfail("Excluded")
    path = ("References", "Profiles", vendor)
    assert path in toc
    v = toc[path].split("/")
    assert v == ["profiles-reference", vendor, "index.md"]


@pytest.mark.parametrize("profile", all_profiles())
def test_profile_doc_exists(profile):
    vendor, name = profile.split(".")
    path = PROFILE_DOCS_BASE / vendor / f"{name}.md"
    assert path.exists(), f"Profile '{profile}' must be documented in {path}"
