# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Fix broken phone parents
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict

from noc.phone.models.phonenumber import PhoneNumber
# NOC modules
from noc.phone.models.phonerange import PhoneRange


def fix():
    # Fix phone ranges with broken parents
    range_id = set()
    parents = defaultdict(list)  # parent -> ids
    for d in PhoneRange._get_collection().find({}, {"_id": 1, "parent": 1}):
        range_id.add(d["_id"])
        if d.get("parent"):
            parents[d["parent"]] += [d["_id"]]
    pset = set(parents)
    for p in pset - range_id:
        for pr in parents[p]:
            r = PhoneRange.get_by_id(pr)
            r.save()
    # Fix phone numbers with broken parents
    nparents = defaultdict(list)
    for d in PhoneNumber._get_collection().find({}, {"_id": 1, "phone_range": 1}):
        if not d.get("phone_range"):
            continue
        nparents[d["phone_range"]] += [d["_id"]]
    pset = set(nparents)
    for p in pset - range_id:
        for pn in nparents[p]:
            n = PhoneNumber.get_by_id(pn)
            n.save()
