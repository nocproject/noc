# ----------------------------------------------------------------------
# Set Link.objects
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import progressbar
import datetime
import time

# NOC modules
from noc.inv.models.link import Link
from noc.sa.models.managedobject import ManagedObject

BATCH_SIZE = 100


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

        time.sleep(1)


def fix():
    max_value = Link.objects.filter().count()
    for link in progressbar.progressbar(iter_ids_batch(), max_value=max_value):
        # for link in Link.objects.filter(id__in=ids).timeout(False):
        try:
            link.update_topology()
            ManagedObject.update_links(link.linked_objects)
        except AssertionError:
            print("Assertion Error, check link with id: %s" % link.id)
        except Exception as e:
            print("Exception : |%s|%s|" % (e, link.id))
