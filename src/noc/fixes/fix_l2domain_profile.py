# ---------------------------------------------------------------------
# Fix l2domain profile
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-pary modules
from bson import ObjectId

# NOC modules
from noc.vc.models.l2domain import L2Domain
from noc.vc.models.l2domainprofile import L2DomainProfile


def fix():
    l2domain_profile_id = L2DomainProfile._get_collection().find_one(
        {"name": "default"}, {"_id": 1}
    )["_id"]
    L2Domain._get_collection().update_one(
        {"_id": ObjectId("61bee7425c42c21338453614"), "name": "default"},
        {"$set": {"profile": l2domain_profile_id}},
        upsert=True,
    )
