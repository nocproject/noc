# ----------------------------------------------------------------------
# inv.ResourceGroup tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.inv.models.resourcegroup import ResourceGroup


def test_clean_leagacy_id():
    left = ResourceGroup._get_collection().find_one({"_legacy_id": {"$exists": True}})
    assert left is None, "_legacy_id field has been left by migration"
