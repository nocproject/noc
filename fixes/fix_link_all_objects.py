# ----------------------------------------------------------------------
# Set Link.objects
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
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
        d = [d["_id"] for d in cursor]
        if not d:
            break
        for link in Link.objects.filter(id__in=d).timeout(False):
            yield link
        # if match and match["_id"]["$gt"] == d[-1]:
        #     break
        match = {"_id": {"$gt": d[-1]}}


def fix():
    max_value = Link.objects.filter().count()
    for link in progressbar.progressbar(iter_ids_batch(), max_value=max_value):
        # for link in Link.objects.filter(id__in=ids).timeout(False):
        try:
            link.save()
        except AssertionError:
            print("Assertion Error, check link with id: %s" % link.id)
