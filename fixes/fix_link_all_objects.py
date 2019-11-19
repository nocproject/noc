# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Set Link.objects
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import progressbar

# NOC modules
from noc.inv.models.link import Link

BATCH_SIZE = 10000


def iter_ids_batch():
    match = {}
    while True:
        print(match)
        cursor = (
            Link._get_collection()
            .find(match, {"_id": 1}, no_cursor_timeout=True)
            .sort("_id")
            .limit(BATCH_SIZE)
        )
        # for d in cursor:
        yield [d["_id"] for d in cursor]
        if match and match["_id"]["$gt"] == d["_id"]:
            break
        match = {"_id": {"$gt": d["_id"]}}


def fix():
    max_value = Link.objects.filter().count() / 10000
    i = 0
    for ids in progressbar.progressbar(iter_ids_batch(), max_value=max_value + 2):
        i += 1
        if i < 20:
            continue
        for l in Link.objects.filter(id__in=ids).timeout(False):
            try:
                l.save()
            except AssertionError:
                print("Assertion Error, check link with id: %s" % l.id)
